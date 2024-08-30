from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, to_timestamp, round, dense_rank, lit
from pyspark.sql.window import Window
import pyspark.sql.functions as F
from datetime import datetime

def create_spark_session():
    return SparkSession.builder \
        .appName("WeatherETL") \
        .getOrCreate()

def transform_weather_data(raw_data):
    spark = create_spark_session()
    
    # Convert raw data to Spark DataFrame
    df = spark.createDataFrame(raw_data)
    
    # Convert datetime string to timestamp
    df = df.withColumn("datetime", to_timestamp(col("datetime")))
    
    # Extract date and time into separate columns
    df = df.withColumn("date", to_date(col("datetime"))) \
           .withColumn("time", to_timestamp(col("datetime")))
    
    # Round temperature to 1 decimal place
    df = df.withColumn("temperature", round(col("temperature"), 1))
    
    # Convert wind speed from m/s to km/h
    df = df.withColumn("wind_speed", round(col("wind_speed") * 3.6, 1))
    
    # Create a unique identifier for each city
    window = Window.orderBy("city_name", "country")
    df = df.withColumn("city_id", dense_rank().over(window))
    
    # Split into fact and dimension dataframes
    fact_columns = ['date', 'time', 'city_id', 'temperature', 'humidity', 'pressure', 'wind_speed']
    fact_df = df.select(fact_columns)
    
    dim_columns = ['city_id', 'city_name', 'country', 'latitude', 'longitude']
    dim_df = df.select(dim_columns).dropDuplicates()
    
    return fact_df, dim_df

def get_latest_batch_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

if __name__ == "__main__":
    # Test data
    test_data = [
        {
            'city_name': 'New York',
            'country': 'US',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'temperature': 22.5,
            'humidity': 60,
            'pressure': 1015,
            'wind_speed': 5.1,
            'datetime': '2023-05-01T12:00:00'
        },
        {
            'city_name': 'London',
            'country': 'GB',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'temperature': 15.3,
            'humidity': 72,
            'pressure': 1008,
            'wind_speed': 4.2,
            'datetime': '2023-05-01T12:00:00'
        }
    ]
    
    fact_df, dim_df = transform_weather_data(test_data)
    print("Fact DataFrame:")
    fact_df.show()
    print("\nDimension DataFrame:")
    dim_df.show()
    
    print(f"\nLatest Batch ID: {get_latest_batch_id()}")
