import click
import os
import pandas as pd
import re


@click.group()
def cli():
    pass


@cli.command()
@click.argument("directory", default=os.getcwd(), type=click.Path(exists=True))
@click.option("--output", default="combined.csv", help="Output CSV file name.")
def combine(directory, output):
    """
    This script searches for all CSV files in the specified directory and its subdirectories,
    standardizes their column names, and combines them into one large CSV file.
    """
    csv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                full_path = os.path.join(root, file)
                click.echo(f"Found CSV file: {full_path}")
                csv_files.append(full_path)

    if not csv_files:
        click.echo("No CSV files found.")
        return

    dataframes = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            df.columns = [
                col.lower().replace(" ", "_") for col in df.columns
            ]  # Standardize column names
            dataframes.append(df)
        except Exception as e:
            print("Issue processing file", e)

    # Remove duplicates based on 'mrn' column if it exists

    combined_df = pd.concat(dataframes)

    if "mrn" in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset="mrn")
        click.echo("Duplicates removed based on 'mrn' column.")

    combined_df.to_csv(output, index=False)
    click.echo(f"Combined CSV created at {output}")


@cli.command()
@click.argument("csv_file", default="combined.csv", type=click.Path(exists=True))
def columns(csv_file):
    """
    This command lists all the columns in the provided CSV file.
    The default file is combined.csv.
    """
    try:
        df = pd.read_csv(csv_file)
        columns = df.columns.tolist()
        click.echo(f"Columns in {csv_file}:")
        for col in columns:
            click.echo(col)
    except Exception as e:
        click.echo(f"Error reading file {csv_file}: {e}")


@cli.command()
@click.argument("column")
@click.argument("csv_file", default="combined.csv", type=click.Path(exists=True))
def sample(csv_file, column):
    """
    This command prints the first ten values of the specified column from the given CSV file.
    The default CSV file is combined.csv.
    """
    try:
        df = pd.read_csv(csv_file)

        if column not in df.columns:
            click.echo(f"Column '{column}' not found in {csv_file}.")
            return

        click.echo(f"First ten values in column '{column}' from {csv_file}:")
        for value in df[column].head(10):
            click.echo(value)
    except Exception as e:
        click.echo(f"Error reading file {csv_file}: {e}")


@cli.command()
@click.argument("column")
@click.argument("regex")
@click.argument("source", default="combined.csv", type=click.Path(exists=True))
@click.argument("output", default=None)
def filter(column, regex, source, output):
    """
    This command applies a regex filter to a specified column of the CSV file,
    and outputs the matching rows to a new CSV file.
    The default CSV file is combined.csv.
    """
    try:
        df = pd.read_csv(source)

        if column not in df.columns:
            click.echo(f"Column '{column}' not found in {source}.")
            return

        pattern = re.compile(regex)

        print(pattern)

        filtered_df = df[
            df[column].astype(str).apply(lambda x: bool(pattern.search(x)))
        ]

        if filtered_df.empty:
            click.echo(f"No matches found in column '{column}' with regex '{regex}'.")
        else:
            output_file = (
                output
                or f"filtered_{os.path.basename(source).replace('.csv', '')}_{column}.csv"
            )
            filtered_df.to_csv(output_file, index=False)
            click.echo(f"Filtered data saved to {output_file}")

    except Exception as e:
        click.echo(f"Error reading file {source}: {e}")


if __name__ == "__main__":
    cli()
