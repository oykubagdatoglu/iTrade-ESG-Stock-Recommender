
from typing import List, Dict, Union, Optional
import csv

from pprint import pprint
from datetime import datetime
import copy
import time
from collections import deque


def bubble_sort(dataset: List["Stock"], modifier: str) -> List["Stock"]:
    """
    A standard implementation of the bubble sort algorithm, without optimization

    :param dataset: The list of stocks to sort
    :param: A selection of which attribute of the Stock class to sort by. Used 
            with either "foundation_year", "score", or "performance"
    
    :returns: The sorted dataset.
    """

    # Keep as long as a swap is made in an iteration
    while True:
        swaps = 0
        for stock in range(len(dataset)-1):
            # Swap adjacent items if necessary
            if getattr(dataset[stock], modifier) < getattr(dataset[stock+1], modifier):
                holder = dataset[stock]
                dataset[stock] = dataset[stock+1]
                dataset[stock+1] = holder
                swaps += 1
        
        if swaps == 0:
            break
    
    return dataset


# Merge sort code adapted from: https://www.w3schools.com/dsa/dsa_algo_mergesort.php
def merge_sort(dataset, modifier):
    """
    A standard implementation of the merge sort algorithm. Sorts based on a 
    specific attribute modifier.
    """
    if len(dataset) <= 1:
        return dataset

    # Splits the data into two parts. Since this will be called recursively,
    # it will keep splitting until all elements are separate.
    middle_pointer = len(dataset) // 2
    leftSide = dataset[:middle_pointer]
    rightSide = dataset[middle_pointer:]
    sortedLeft = merge_sort(leftSide, modifier)
    sortedRight = merge_sort(rightSide, modifier)

    # This will effectively sort the individual elements after they have been
    # completely separated
    return merge(sortedLeft, sortedRight, modifier)

def merge(leftList, rightList, modifier):
    """
    Merges two sorted lists into one.

    :param: leftList (List[object]) The left sorted list to be merged.
    :param: rightList (List[object]) The right sorted list to be merged.
    :param: modifier (str) The attribute name of the object to sort by.
    
    :returns: The merged and sorted list.
    """

    finalList = []
    left_pointer = 0
    right_pointer = 0

    # Apply the pointer sorting technique to merge the two lists
    while left_pointer < len(leftList) and right_pointer < len(rightList):
        if getattr(leftList[left_pointer], modifier) >= getattr(rightList[right_pointer], modifier):
            finalList.append(leftList[left_pointer])
            left_pointer += 1
        else:
            finalList.append(rightList[right_pointer])
            right_pointer += 1

    # Add any remaining elements
    finalList.extend(leftList[left_pointer:])
    finalList.extend(rightList[right_pointer:])

    return finalList


# A variable used to switch between the sorting algorithms more easily
SORTING_ALGORITHM = merge_sort


class PreferenceSettings:
    """
    A class that manage settings for ESG, industry ranking, and establishment year according to
    what the user chooses.

    Attributes:
        TH_LOWER (int): The lower bound for the establishment year threshold.
        TH_UPPER (int): The upper bound for the establishment year threshold.
        esg (bool): Used to represent whether the ESG preference is enabled.
        highest_in_industry (bool): Represent whether the "Highest in the Industry" preference is enabled.
        establishement_year (bool): Represents whether the establishment year preference is enabled.
        threshold (Union[int, None]): The threshold year (if establishement_year is enabled). It is set to
                                      None by default.
    """

    TH_LOWER = 1700
    TH_UPPER = datetime.now().year

    def __init__(self):
        """
        Initializes a PreferenceSetting object and prints the main menu

        :returns: No return.
        """
        self.esg: bool = False
        self.highest_in_industry: bool = False
        self.establishement_year: bool = False
        self.threshold: int = None

        self.s_weight: float = None
        self.e_weight: float = None
        self.g_weight: float = None

        self.main_menu()

    def main_menu(self) -> None:
        """
        Prints the main menu options for the user to select from.

        :returns: No return.
        """
        print("\nAvailable preference settings:")
        print("1. ESG Preference setting")
        print("2. Highest in the industry")
        print("3. Establishment year")
        print("Please enter 1, 2, or 3 to select which preference setting you would like to enable.")
        print("Entering an enabled preference setting will disable it.")
        print("Type 'next' or hit enter to continue.\n")
    
    def ask(self) -> Optional[int]:
        """
        Prompts the user to select a preference setting. Also prints a message informing the
        user of their choice.

        :return: -1 once the user decides to continue to the next prompt.
        """
        preference_setting_choice: Union[int, str] = input("Enter your choice here: ")

        # Validate user's choice of preference setting
        if preference_setting_choice not in ("1", "2", "3", "next", ""):
            raise ValueError

        # ESG preference setting was turned on so set the esg attribute to
        # True and print a confirmation message
        if preference_setting_choice == "1":
            if self.esg:
                self.esg = False
                print("ESG preference setting turned OFF successfully!")
            else:
                while True:
                    try:
                        self.s_weight = float(input("Please weight for 'Social' parameter: "))
                        self.g_weight = float(input("Please weight for 'Governance' parameter: "))
                        self.e_weight = float(input("Please weight for 'Environment' parameter: "))
                        break
                    except Exception as e:
                        print("ESG values have to be floats, start again...")

                self.esg = True
                print("ESG preference setting turned ON successfully!")
        
        # Highest in industry preference setting was turned on so set the 
        # highest_in_industry attribute to True and print a confirmation message
        if preference_setting_choice == "2":
            if self.highest_in_industry:
                self.highest_in_industry = False
                print("Highest in industry preference setting turned OFF successfully!")
            else:
                self.highest_in_industry = True
                print("Highest in industry preference setting turned ON successfully!")
        
        # Establishement year filter preference setting was turned on so set the 
        # establishement_year attribute to True and print a confirmation message
        if preference_setting_choice == "3":
            if self.establishement_year:
                self.establishement_year = False
                self.establishement_year_threshold = None
                print("Establishement year preference setting turned OFF successfully!")
            # If the establishement year was False, prompt the user for a threshold and print
            # a confirmation message.
            else:
                self.threshold = int(input("Please enter the establishement year threshold: "))

                # Validate the given threshold
                if not self.TH_LOWER <= self.threshold <= self.TH_UPPER:
                    print(f"Threshold year not within valid range (between 1700 and {self.TH_UPPER})")
                else:
                    self.establishement_year = True
                    print(f"Establishement year preference setting turned ON successfully with threshold {self.threshold}.")
        
        if preference_setting_choice == "next" or preference_setting_choice == "":
            return -1


class Stock:
    """
    Represents a stock and its associated data

    Attributes:
        name (str): The name of the stock.
        performance (float): The return on investment of the stock per $100.
        industry (str): The industry to which the stock belongs.
        foundation_year (int): The year the company was founded.
        environment (Union[int, float]): The stock's environmental score.
        social (Union[int, float]): The stock's social score.
        governance (Union[int, float]): The stock's governance score.
        score (Union[int, float]): The overall score of the stock, initially set to performance.
    """
    def __init__(self, name: str, performance: float, industry: str, 
                 foundation_year: int, e: float, s: float, g: float) -> None:
        self.name = name
        self.performance = performance
        self.industry = industry
        self.foundation_year = foundation_year
        self.environment = e
        self.social = s
        self.governance = g

        # The score is initialized to be the same as the performance (ROI) but if the
        # user selects the ESG preference setting, then the score formula is applied as
        # described in the StockDatabase class.
        self.score = performance

        self.score_changed = False

    def set_score(self, new_score):
        self.score_changed = True
        self.score = new_score

    def __str__(self) -> str:
        """
        Returns a string representation of the stock.

        :returns: String representation of the stock containing this info: name, 
                  foundation year, and ROI.
        """        
        # If the ESG setting is on, return a different string representation
        if self.score_changed:
            return (f"Stock name: {self.name}, Founded in {self.foundation_year}. "
                    f"ROI: ${self.performance:.2f} per $100. "
                    f"Total Score: {self.score:.2f}")

        return f"Stock name: {self.name}, founded {self.foundation_year}. Trading with an ROI of ${self.performance} per $100."

    def __repr__(self) -> str:
        """
        Returns a string representation of the stock.

        :returns: String representation of the stock containing this info: name, 
                  foundation year, and ROI.
        """
        return f"Stock name: {self.name} ({self.industry}), founded {self.foundation_year}.ROI of: ${self.performance} per $100"



class StockDatabase:
    """
    Represents a database that stores all the Stock objects. Also contains several
    methods for manipulation and filtering of the database.

    Attributes:
        dataset (List[Stock]) -> Used to store the Stock objects.
        industried_dataset (Dict[str, List[Stock]]) -> Used to store the stock objects
                                grouped by their industry in this format - key: industry, value:
                                a list of Stock objects belonging to that industry
        raw_stock_data (List[Dict[str, Union[str, float, int]]]) -> Stores the raw stock data
                             in this format - List of dicts where keys are the columns of the CSV file
                             and the values are the stock's values for that column.
        csv_path (Optional[str]) -> The path to the CSV file containing the data.
    """
    def __init__(self) -> None:
        """
        Initializes a database object.

        :returns: No return.
        """
        self.dataset: List[Stock] = []
        self.industries_dataset: Dict[str, List[Stock]] = {}
        self.raw_stock_data: List[Dict[str, Union[str, float, int]]] = None
        self.csv_path: Optional[str] = None

    def get_original_database(self) -> List[Stock]:
        """
        Returns the database as it is right after parsing the CSV data,
        without any filters or constraints.

        :returns: A list of stocks representing the data in the untouched data 
                  in the original dataset.
        """
        return self.create_stock_objects()

    def set_csv_path(self, path: str) -> None:
        """
        Changes the path to the CSV dataset.
        :param path: The path to change to
        
        :returns: No return.
        """
        self.csv_path = path

    def get_stock_data(self) -> None:
        """
        Read the CSV file containing the stocks information and store it in a list of dictionaries - the
        self.raw_stock_data attribute.
        Since DictReader reads all content as a string, apply type conversion when reading the data 
        where necessary.

        :returns: No return. 
        """
        # Use a try block to attempts to open a file. If the file doesn't exist or
        # is corrupted, this will throw an error.
        try:
            with open(self.csv_path, mode='r', encoding='utf-8') as file:
                # Read the data in the csv file and store it in a dictionary
                file_data = csv.DictReader(file)
                # Will be used to store the stock objects based on the CSV file data
                stock_data: List[Dict[str, Union[str, float, int]]] = []
                
                # Create stock objects and append them to the above list
                for row in file_data:
                    # Use a try block to attempt the type conversions
                    try:
                        row["Performance"] = float(row["Performance"])
                        row["FoundationYear"] = int(row["FoundationYear"])
                        row["Environment"] = int(row["Environment"])
                        row["Social"] = int(row["Social"])
                        row["Governance"] = int(row["Governance"])
                        stock_data.append(row)

                    except (ValueError, KeyError) as e:
                        print(f"Error processing row {row}: {e}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            stock_data = []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            stock_data = []

        self.raw_stock_data = stock_data


    def create_stock_objects(self) -> List[Stock]:
        """
        Store stocks in a list where each element is a Stock object
        
        :returns: A list of Stock objects, this is sometimes used in the 
                  function calls and sometimes not.
        """
        self.get_stock_data()

        # Make sure dataset is clear so that if this function is called twice, it doesn't
        # append the data twice
        self.dataset.clear()

        # Create stock objects from the raw data and append them to the database
        for stock in self.raw_stock_data:
            name = stock["ID"]
            price = stock["Performance"]
            industry = stock["Industry"]
            year = stock["FoundationYear"]
            e = stock["Environment"]
            s = stock["Social"]
            g = stock["Governance"]

            stock_object = Stock(name, price, industry, year, e, s, g)
            self.dataset.append(stock_object)
        
        return self.dataset

    def assign_score_and_sort(self, e_weight: float, s_weight: float, g_weight: float) -> None:
        """
        This method gets called if the "ESG score" preference setting is on.

        :param e_weight: Weight for environment criterion
        :param s_weight: Weight for social criterion
        :param g_weight: Weight for governance criterion

        :returns: No return.
        """

        # Assign a "score" value to every stock using this formula:
        # score = e * e_weight + s * s_weight + g * g_weight
        for stock in self.dataset:
            stock.set_score(round(stock.performance + \
                            stock.environment * e_weight + \
                            stock.governance * g_weight + stock.social * s_weight, 1))
    
        # Sort the dataset using the score attribute
        self.dataset = SORTING_ALGORITHM(self.dataset, "score")


    def restructure_ds_by_industry(self, dataset_section: Optional[List[Stock]]=None) -> None:
        """
        Restructures the dataset to be grouped by industry and stores the new
        dictionary in a new dataset.

        :param dataset_section: If a dataset is given as parameter, it will restructure
                                this dataset instead of the global one
        
        :returns: No return.
        """
        # A dictionary containing the indiviudal industries as keys and the stocks
        # belonging to those industries as values (in a list)
        self.industries_dataset = {}

        # Populate industries dictionary.
        if not dataset_section:
            for stock in self.dataset:
                if stock.industry not in self.industries_dataset.keys():
                    self.industries_dataset[stock.industry] = []
                self.industries_dataset[stock.industry].append(stock)
        else:
            for stock in dataset_section:
                if stock.industry not in self.industries_dataset.keys():
                    self.industries_dataset[stock.industry] = []
                self.industries_dataset[stock.industry].append(stock)

        return self.industries_dataset


    def apply_industry_sort(self, top_n: int, est_thresh: int=None) -> None:
        """
        This method gets called if the "Highest in industry" preference setting is on.

        :param top_n: The combined number of stocks to find, distributed evenly between all the industries
        :param ESG_preference: Whether the user selected the ESG preference setting to be ON or OFF.

        :return: No return.
        """

        # Algorithm

        # 1.) Group the stocks by industry
        # 3.) Filter each industry's stock by establishement year if available
        # 2.) Apply sort to each industry's reamining stocks
        # 4.) Pick top_n stocks from each industry
        #         - If this results in a number of stocks lower than top_n,
        #           repeat steps 3 and 4 with a higher establishement year.

        # Group stocks by industry
        self.industries_dataset: Dict[str, Stock] = self.restructure_ds_by_industry()

        # Filter each industry's stock by establishement year if available
        def filter_using_est_year(dataset, threshold):
            for industry, stocks in dataset.items():
                dataset[industry] = [stock for stock in stocks if stock.foundation_year <= threshold]

            return dataset

        def sort_remaining_stocks(dataset):
            # Sort the each industry's filtered set of stocks
            for industry, stocks in dataset.items():
                dataset[industry] = SORTING_ALGORITHM(stocks, "score")
            
            return dataset

        # Only filter if the establishement year setting is on
        if est_thresh is not None:
            self.industries_dataset = filter_using_est_year(self.industries_dataset, est_thresh)

        # Sort the remaining stocks
        self.industries_dataset = sort_remaining_stocks(self.industries_dataset)

        # Pick the top_n stocks from each industry
        """
            Algorithm for distributing evenly:
                1.) Loop throught the stocks in each each industry
                2.) Pop the top stock
                3.) Keep a counter of how many stocks have been popped
                4.) Once this counter reaches top_n, end the loop.
                    If a IndexError is thrown when popping the value,
                    it means we have to repeat the filtering and sorting again
                    with a higher threshold value.
        """

        picked_stocks = []
        iterations = 1
        threshold_changed = False
        while len(picked_stocks) < top_n:
            for industry, stocks in self.industries_dataset.items():
                # A deque is used because it has a O(1) .popleft() time
                # as opposed to .pop(0) which has O(n)
                if not isinstance(stocks, deque):
                    self.industries_dataset[industry] = deque(stocks)
                    stocks = self.industries_dataset[industry]
                try:
                    top_stock = stocks.popleft()
                    picked_stocks.append(top_stock)
                except IndexError as e:
                    # Not enough stocks, have to increase threshold by 1 year and try again.
                    self.industries_dataset: Dict[str, Stock] = self.restructure_ds_by_industry()
                    self.industries_dataset = filter_using_est_year(self.industries_dataset, est_thresh+iterations)
                    self.industries_dataset = sort_remaining_stocks(self.industries_dataset)
                    picked_stocks.clear()
                    threshold_changed = True
                    break
            
            iterations += 1
        
        if threshold_changed:
            print(f"\nWARNING: Not enough stocks, increasing year threshold to {max(picked_stocks, key=lambda k: k.foundation_year).foundation_year}.")

        self.dataset = picked_stocks


    def apply_establishment_year_filter(self, top_n: int, threshold_year: int) -> None:
        """
        This method gets called if the "Establishment year" preference setting is on and the highest
        in industry setting is off. It filters the dataset using the threshold year. If not enough 
        stocks are in the resulting set, increase the threshold year by 1 year. Continue doing 
        this until the dataset is populated enough.

        :param top_n: The combined number of stocks to find, distributed evenly between all the industries
        :param threshold_year: The maximum year to allow in the dataset.

        :return: No return.
        """
        increase_threshold: bool = False
        iterations = 0
        # Keep looping until enough stocks are generated
        while not increase_threshold:
            self.dataset = self.get_original_database()
            self.dataset = SORTING_ALGORITHM(self.dataset, "score")
            filtered_dataset: List[Stock] = [stock for stock in self.dataset if stock.foundation_year <= threshold_year + iterations]

            # Stop condition
            if len(filtered_dataset) >= top_n:
                increase_threshold = True

            if iterations == 300:
                return
            
            # Used to increase the current threshold year
            iterations += 1

        # Print a warning message to inform the user
        if increase_threshold:
            print(f"\nWARNING: Not enough stocks, increasing year threshold to {threshold_year + iterations - 1}.")

        self.dataset = filtered_dataset[:top_n]



def main() -> None:
    """
    The main function that puts all the functionality together. First, user input is gathered,
    then the database is created. After that, the preference settings are applied and the
    result is printed.

    :returns: No return.
    """
    preferences = PreferenceSettings()

    # Ask the user for input on which preference settings to use
    # While loops are used for validation
    while True:
        try:
            preference_choice = preferences.ask()
            if preference_choice == -1:
                break
        except ValueError:
            print("You have to enter a valid preference setting")

    # Ask user for input of n highest performing stocks
    while True:
        try:
            top_n: int = int(input("Please enter how many stocks you would like to be recommended: "))
            if not 1 <= top_n <= 100:
                print("The number has to be between 1 and 100")
                continue
            break
        except ValueError:
            print("The value has to be an integer!")

    # Create the database that will store and manipulate all the stock data
    database = StockDatabase()
    database.set_csv_path("stocks.csv")
    # database.set_csv_path("expanded.csv")
    # Transform CSV data into objects of type Stock
    database.create_stock_objects()

    # A list containing the active preference settings. This is used later to give
    # a nicer message to the user.
    ON_preference_settings: List[str] = []

    start_time = time.time()

    if preferences.establishement_year:
        ON_preference_settings.append("establishement year")

    # Check which pereference settings were activated by the user
    # If the ESG settings is on...
    if preferences.esg:
        # ...sort the database by score
        database.assign_score_and_sort(s_weight=preferences.s_weight, g_weight=preferences.g_weight, e_weight=preferences.g_weight)
        ON_preference_settings.append("ESG criteria")
    # If the highest in industry setting is on...
    if preferences.highest_in_industry:
        # ...pick the total top_n equally from each industry
        database.apply_industry_sort(top_n, est_thresh=preferences.threshold)
        ON_preference_settings.append("highest in industry")
    else:
        # If the establishemen_year is on and highest in industry isn't...
        if preferences.establishement_year:
            # Remove all stocks that are above the threshold from the database
            database.apply_establishment_year_filter(top_n, preferences.threshold)
    # If all preference settings are OFF...
    if not preferences.esg and not preferences.establishement_year and not preferences.highest_in_industry:
        # ...simply sort the dataset by performance and get the top n stocks  
        database.dataset = SORTING_ALGORITHM(database.dataset, "performance")[:top_n]
        ON_preference_settings.append("no")

    # Print a message if the stocks in each industry aren't roughly equal for whatever reason
    if preferences.highest_in_industry:
        industries = database.restructure_ds_by_industry()
        # print(industries)
        longest = len(industries[max(industries, key=lambda k: len(industries[k]))])
        shortest = len(industries[min(industries, key=lambda k: len(industries[k]))])
        if abs(longest - shortest) >= 2:
            print("\nWARNING: Could not find a good ditribution of stocks given the restrictions.\n")

    
    end_time = time.time()

    output_string: str = f"Here are the top {min(len(database.dataset), top_n)} stocks, grouped by industry, with"

    # Print a nice message to the user
    if len(ON_preference_settings) == 2:
        print(f"\n{output_string} the {' and '.join(ON_preference_settings)} preference setting(s) on: \n")
    else:
        print(f"\n{output_string} the {', '.join(ON_preference_settings)} preference setting(s) on: \n")

    # If the ESG setting is on, print the chosen weights
    if preferences.s_weight:
        print(f"\nSocial weight (S): {preferences.s_weight}")
        print(f"Governance weight (G): {preferences.g_weight}")
        print(f"Environment weight (E): {preferences.e_weight}\n")

    # Used to print the stocks under their corresponding industry
    restructed_database = database.restructure_ds_by_industry(database.dataset[:top_n])

    # Print the stocks grouped by industry
    counter = 1
    for industry, stocks in restructed_database.items():
        print(f"{industry.capitalize()}:")
        for stock in stocks:
            print(f"{counter}. {str(stock)}")
            counter += 1
        print("\n")

    if len(database.dataset) < top_n:
        print("\nThe dataset doesn't contain enough stocks to satisfy the criteria.")

    print(f"\nSorting finished in: {end_time-start_time:.6f} seconds")

if __name__ == "__main__":
    main()

