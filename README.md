# Reddit ELT Pipeline

Welcome to the **Reddit ELT Pipeline** repository! This project aims to provide an end-to-end data pipeline for extracting data from Reddit, transforming it, and visualizing insights. The pipeline is designed not only to create a dashboard but also to serve as a learning opportunity by utilizing a variety of tools and technologies.

## Overview

The Reddit ELT Pipeline involves extracting Reddit data from its API, processing it, and ultimately creating visualizations using Power BI. The pipeline is orchestrated using Apache Airflow and Docker. The data is extracted using the PRAW API wrapper in Python, transformed using dbt, and then loaded into AWS Redshift for analysis.

![workflow](https://github.com/Ayoub-Talbi1/Reddit-ELT/assets/86127094/660c22c9-4459-4d76-923f-0177437b3023)



## How the Pipeline Works

The pipeline consists of several key components:

1. **Data Extraction (Airflow/DAG)**:
   - The extraction process is controlled by the `ELT_reddit_pipeline.py` DAG within the `dags` folder of the `airflow` directory.
   - The `extract.py` script interacts with the Reddit API using the PRAW library, pulling data from the past 24 hours.
   - Extracted data is stored in a CSV file with fields like post ID and author name.
   - The `upload_s3.py` script uploads the CSV to an AWS S3 bucket for cloud storage.
   - The `upload_redshift.py` script copies the data from S3 into AWS Redshift for further analysis.
   - The `validation.py` script provided in the extraction folder is responsible for validating input parameters. It ensures that the input date is in the correct format (YYYYMMDD).

2. **Data Transformation (dbt)**:
   - Data transformation is managed using dbt (data build tool). Transformation tasks are not orchestrated with Airflow but are run separately.
   - The `dbt` folders, added to the repo after connecting it to dbt Cloud, contains transformation logic, I only added a model (text_posts.sql) and schema.yml under the models folder, and did the transformations I want (here I did a simple transformation of choosing only the columns I want), the schema.yml did some basic tests and documentation for our table. I haven't added much, as it's mostly for demonstration purposes. You can see that I've added a not_null test for id. For the rest, I've only added in the name of the column and a description, I didnt work with the other folders.
   - Under dbt_project.yml all I've really changed here is the project name to reddit_project and told dbt to create all models as tables (rather than views). 
   - dbt is used to connect to the data warehouse (Redshift) and apply transformations to the data.
   - ![Capture d’écran 2023-08-17 145512](https://github.com/Ayoub-Talbi1/Reddit-ELT/assets/86127094/413b69c2-5e6a-4410-a2fd-3c64551686d9)

3. **Data Visualization (Power BI)**:
   - Power BI is connected to the data warehouse to create visualizations and gain insights from the transformed data.
   - ![Capture d’écran 2023-08-29 174628](https://github.com/Ayoub-Talbi1/Reddit-ELT/assets/86127094/27567aba-acda-4f2f-ba4e-546bf1943987)

4. **Infrastructure as Code (Terraform)**:
   - The infrastructure for the pipeline is defined using Terraform, with the configuration stored in the `terraform` directory.
   - `main.tf` contains the main infrastructure setup, and `variables.tf` contains variable definitions.
   - **Initialize Terraform**: Open a terminal in the `terraform` directory and run the following command to initialize Terraform:

   ```sh
   terraform init
   ```

   This command initializes Terraform and downloads the necessary providers based on the configuration files.

   - **Preview Changes (Optional)**: Run the following command to see a preview of the resources that Terraform will create:

   ```sh
   terraform plan
   ```

   This step allows you to review the changes that Terraform will apply before actually creating the resources.

   - **Apply Changes**: To provision the resources defined in the Terraform configuration, run the following command:

   ```sh
   terraform apply
   ```

   Terraform will prompt you to confirm the changes before proceeding. Type `yes` to apply the changes.

   - **Resource Provisioning**: Terraform will now provision the specified resources on AWS according to your configuration.

   - **Resource Deletion**: To tear down the resources created by Terraform, you can run the following command:

   ```sh
   terraform destroy
   ```

5. **Airflow Container (Docker)**:
   - The Apache Airflow environment is containerized using Docker, with the configuration defined in the `docker-compose.yaml` file.
   - This eliminates the need for manual Airflow setup.


## Getting Started

To set up and run the Reddit ELT Pipeline, follow these steps:

1. Configure your Reddit API credentials in the `extract.py` script.
2. Set up your AWS credentials for S3 and Redshift in the `upload_s3.py` `upload_redshift.py`.
3. Configure your Terraform variables in the `variables.tf` file.
4. Run Terraform to provision the necessary infrastructure.
5. Start the Airflow environment using Docker Compose.
6. Run the `ELT_reddit_pipeline.py` DAG in Airflow to trigger the pipeline.
7. Use dbt to perform data transformations.
8. Connect Power BI to the data warehouse for visualization.

Feel free to explore and adapt the pipeline according to your needs. If you encounter any issues or have questions, please refer to the documentation or reach out for assistance.

Happy data pipelining! 🚀
