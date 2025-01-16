# Covariance Matrix Visualization  

This project visualizes covariance matrices of stock returns, building upon my other [Black-Litterman-Implied-Covariance project](https://github.com/samueldecornez62/Black-Litterman-Implied-Covariance) for its data source. The application works well on local devices but is not yet publicly deployable.  

This website allows users to select one or more industries from the dropdown menu that subdivide this universe of 9,782 stocks from a dropdown menu. The covariance matrix for the associated stocks will then be displayed on the page. See above-linked project for detailed explanation of industry classification. 

You can zoom into any section of the matrix by dragging your cursor over the desired region. Hovering your mouse over any cell indicates which specific stocks are being viewed, as well as the value of the covariance. There is also a button to reset the zoom.

Additionally, there is a second dropdown menu that changes the color palette used to display the matrices. 

Lastly, the website displays CSV file download buttons to download the data in the matrices. These download links appear below the matrices, in order they are displayed. The download links currently do not work even locally, since the website is not yet fully public (see below for more details). 

**To run the visualization locally:**  
1. Install all files into the same directory.  
2. Open the command prompt, navigate to the folder, and run:
   ```python more_test.py```
3. Wait for the local link to load in command prompt and open it in your browser


## Project Overview

### Key Files
- ```more_test.py```
  The first version where the visualization worked well and was ready as a first iteration of local deployment
- ```final_dash.py```
  The latest attempt to deploy the app as a public website using Docker and Heroku

### Supporting Files 
- ```website_builder_1.ipynb```
  Contains tests for loading pickles, generating plots, and sorting data. It references data prepared in the [Black-Litterman-Implied-Covariance project.](https://github.com/samueldecornez62/Black-Litterman-Implied-Covariance)

- ```downsize_pickle.ipynb```
  Downsized the pickle files to fit Heroku's free dyno limits and not incur any unnecessary charges

### Deployment Files 
- ```requirements.txt```: Specifies the Python dependencies for the project.
- ```.dockerignore```: Lists files to exclude during Docker builds.
- ```Dockerfile```: Contains all setup instructions for building a containerized version of the app, including installing dependencies, copying files, exposing ports, and running the app.

### App Progress and Tests Folder
This folder contains older iterations and test versions. It is not necessary and can be ignored.



## Current Status and Next Steps
- **Current status:**
  The visualization app functions well locally but has not been fully deployed as a public website.
- **Next Steps:**
  Deploying the app publicly using final_dash.py, Docker to create a container able to store the full sized large pickle files, and Heroku for deployment, remains the goal. Once the website is deployed successfully, the data will be stored directly on the website through the Docker container, and the CSV download links should work correctly. 



