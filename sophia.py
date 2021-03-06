import pandas as pd
import numpy as np
import time
from user_use_behavior import get_tableau_raw_data_from_source
from user_use_behavior import get_metrics_columns_name


def user_summaries(users=pd.DataFrame,summary_key=""):
    return users.groupby(summary_key)["user_id"].apply(set).apply(len)


def aggregate_to_week(source=pd.DataFrame, dims=[],columns=[]):
    return source.groupby(dims)[columns].aggregate(np.sum).reset_index()


def fcf_calculator(source=pd.DataFrame):

    source["fcf_short"] = source["net_income"] + source["capital_expenditure"]
    source["fcf_middle"] = source["net_income"] + np.cumsum(source["capital_expenditure"])
    source["fcf_long"] = np.cumsum(source["net_income"]) + np.cumsum(source["capital_expenditure"])

    tmp = np.cumsum(source["capital_expenditure"])
    source["fcf_middle_rolling_4w"] = source["net_income"] + source["capital_expenditure"].rolling(4).sum().fillna(0)

    for i in range(4):
        source.set_value(i, "fcf_middle_rolling_4w", source["net_income"][i] + tmp[i])

    source["fcf_middle_4w_smooth"] = source["fcf_middle_rolling_4w"].rolling(window=2, min_periods=1, center=False).mean()

    return source

if __name__ == "__main__":

    t1 = time.time()

    gio_files = ["./0515/20170201-20170515_user_访问量&访问时长.csv",
                 "./0515/20170201-20170515_FQY_主要功能数据_U_user_table_PV浏览类.csv",
                 "./0515/20170201-20170515_FQY_主要功能数据_U_user_table_action交互类.csv"]

    result = get_tableau_raw_data_from_source(files=gio_files, user_max_id=67353)
    result = result[result.week_iso != 52]

    dims = ["week_iso", "org_name", "level", "industry", "pay_status", "sim_date"]

    result_by_week = aggregate_to_week(source=result,dims=["week_iso"],columns=get_metrics_columns_name())

    source = fcf_calculator(result_by_week)

    t2 = time.time()

    print(t2 - t1)

    print(source[["fcf_short", "fcf_middle", "fcf_long", "fcf_middle_rolling_4w","fcf_middle_4w_smooth"]])

    print("Done")











