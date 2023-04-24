from last_isw import get_last_isw_matrix
from weather import get_weather
import numpy
import scipy


def get_matrix(region="all"):
    weather_df = get_weather(region)
    weather_df = weather_df.drop(columns=["location", "time", "date", "region_id", "hour_conditions"], axis=1)
    last_isw_matrix = get_last_isw_matrix().toarray()
    # print(weather_df.shape)

    repeated_matrix = numpy.repeat(last_isw_matrix, weather_df.shape[0], axis=0)
    # print(repeated_matrix)
    repeated_matrix = scipy.sparse.csr_matrix(repeated_matrix)
    # print(repeated_matrix)
    merged_matrix = scipy.sparse.hstack((repeated_matrix, weather_df), format="csr")
    print(merged_matrix.shape)
    return merged_matrix


if __name__ == "__main__":
    get_matrix("Sumy")
