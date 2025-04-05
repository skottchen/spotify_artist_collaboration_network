from extract_api_data import extract_api_data
from clean_json_files import clean_json_files
from perform_network_analysis import perform_network_analysis


def main():
    extract_api_data()
    clean_json_files()
    perform_network_analysis()


if __name__ == "__main__":
    main()
