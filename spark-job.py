import os
from pyspark.sql import SparkSession


def main():
    bucket = os.environ["S3_BUCKET"]

    input_path = f"s3a://{bucket}/titanic.csv"
    output_path = f"s3a://{bucket}/landing/titanic/"

    spark = (
        SparkSession.builder
        .appName("SparkApplicationJob")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        df = (
            spark.read
            .format("csv")
            .options(
                header="true",
                inferSchema="true",
                delimiter=";"
            )
            .load(input_path)
        )

        df.show()
        df.printSchema()

        (
            df.write
            .mode("overwrite")
            .format("parquet")
            .save(output_path)
        )

        print("Successfully written")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()