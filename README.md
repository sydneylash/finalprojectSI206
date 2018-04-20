# finalprojectSI206

# finalprojectSI206

1.	Data sources used, including instructions for a user to access the data sources (e.g., API keys or client secrets needed, along with a pointer to instructions on how to obtain these and instructions for how to incorporate them into your program (e.g., secrets.py file format))

	I chose to use Broadway.com for this project, where I crawled and scraped multiple pages in this site. I have not used this site before. The link for the website is https://www.broadway.com/. 

2.	Any other information needed to run the program (e.g., pointer to getting started info for plotly)

	For this project, I used plotly to create my visualizations. Plotly requires a login to access my visualizations. Here are the instructions for getting started on plotly:
	 -Create an account by creating a username and password. In addition, you will need to install plotly for Python by typing "pip install plotly" on your terminal. Once that is done, you can set your credentials by running the following lines in terminal:

	 	import plotly
	 	plotly.tools.set_credentials_file(username='YOUR_USERNAME', api_key='YOUR API KEY')

	 -For complete directions on using plotly in Python, here is the link: https://plot.ly/python/getting-started/ 
	 
3.	Brief description of how your code is structured, including the names of significant data processing functions (just the 2-3 most important functions--not a complete list) and class definitions. If there are large data structures (e.g., lists, dictionaries) that you create to organize your data for presentation, briefly describe them.

	I start my code by creating a database using sql. I create the two different tables within my database, titled Shows and ShowTimes. Then, I create the cache, where data from the site will be stored. Next I create my first function (get_show_lst) to return a dictionary named title_link where the keys are the show titles and the values are the show links. The function crawls through each page of the website depending on the entered category. From there, I scraoe through different elements to access the title and link of a particular show and add this to title_link.

	The next part of my code includes my class, where the show name, opening date, preview date, address, and runtime can be displayed to the user using the str method. The next function, get_shows, populates the database by crawling and scraping the different information.
	The next part of my code includes 4 functions getShowsbyOpeningDate, getRunTimes, getShowTimes, and getShowsbyPreviewMonth. The code within each function uses plotly to create various graphs.

4.	Brief user guide, including how to run the program and how to choose presentation options.

	The first thing that the user will be asked for is to enter a command. The user must enter the word category, followed by the category type (broadway, off-broadway, musical, play, etc.) and the shows in the category will be returned. From there, the user may enter another command “info” followed by the number of whatever show they are seeking information about. This will then give the user the runtime, preview date, and opening date of the selected show.

	Next, if the user enters 1, plotly will be prompted to display a bar graph of the shows by their opening year. If the user enters 2, plotly will prompt a pie chart of shows by their runtime.If the user enters 3, plotly will prompt a scatter plot of the shows by their runtime and show time. Lastly, if the user enters 4, plotly will prompt a bar graph of the shows by their preview month. 

	If the user wishes to exit the code, he or she will simply type "exit." 

