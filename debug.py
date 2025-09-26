import csv
import os

def remove_empty_row_descriptions(csv_file_path):
    """
    Removes rows from a CSV file where the 'description' column is empty.

    Args:
        csv_file_path (str): The path to the CSV file.
    """

    # Create a temporary file to store the filtered data
    temp_file_path = csv_file_path + ".tmp"

    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as infile, \
             open(temp_file_path, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader, None)  # Read the header row
            if header:
                writer.writerow(header)  # Write the header to the output file

                # Determine the index of the 'description' column.  This is crucial.
                try:
                    row_description_index = header.index('Description')
                except ValueError:
                    print("Error: 'description' column not found in the header.")
                    os.remove(temp_file_path)  # Clean up the temp file
                    return  # Exit the function

                for row in reader:
                    # Check if the 'description' column is empty.  Handle potential index errors.
                    try:
                        if row[row_description_index].strip():  # Check for non-empty string after removing whitespace
                            writer.writerow(row)
                    except IndexError:
                        print(f"Warning: Row with fewer columns than expected encountered. Skipping row: {row}")
                        continue # Skip the row if it doesn't have enough columns

        # Replace the original file with the filtered data
        os.remove(csv_file_path)
        os.rename(temp_file_path, csv_file_path)

        print(f"Successfully removed rows with empty 'description' from {csv_file_path}")

    except FileNotFoundError:
        print(f"Error: File not found: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Clean up the temp file if an error occurred
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# Example usage:
if __name__ == "__main__":
    file_path = "Zillow_NY_26_Sep_25.csv"  # Replace with the actual path to your CSV file
    remove_empty_row_descriptions(file_path)