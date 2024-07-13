# Ultrasonic Sensor Characterization for Autonomous Cars

## Motivation

This project aims to assist the University of Toronto's Mechatronics course (MIE 444) students who are developing autonomous cars using sensors. Students have reported issues with sensors, particularly ultrasonic sensors. This feedback motivated us to undertake a project to characterize these sensors. Our goal is to cluster similar sensors, identify anomalies such as defective sensors, and ensure high-quality data collection. Additionally, this project will also benefit manufacturing companies like Magna, which rely on high-quality sensors for various applications in autonomous vehicles.

## Project Overview

To investigate these questions, we first need to obtain quality data. We developed a system that integrates Arduino and Python to automate data collection and ensure consistent results. The steps of our project include:

1. **Data Collection**: We built a system using Arduino and Python to collect high-quality data from ultrasonic sensors. This system automates the data collection process, ensuring consistency and reliability.
2. **Exploratory Data Analysis (EDA)**: We performed EDA to understand the data, identify patterns, and inform the next steps in our analysis.
3. **Feature Engineering**: Based on the findings from EDA, we engineered features that help in characterizing the sensors.
4. **Feature Selection**: We selected the most relevant features for further analysis.
5. **Sensor Characterization**: Using the selected features, we applied various techniques to characterize the sensors. These techniques include:
   - **Machine Learning**: Techniques such as autoencoders to identify patterns and anomalies.
   - **Dimensionality Reduction**: Methods like Principal Component Analysis (PCA) to reduce the feature space and highlight significant variations.

## Repository Contents

This GitHub repository contains the following:

- **Data Collection Code**: Arduino and Python code for automating the data collection process.
- **Ultrasonic Data**: Collected data from ultrasonic sensors.
- **Analysis Effort**: Jupyter notebooks and scripts for EDA, feature engineering, feature selection, and sensor characterization.

## Getting Started

To get started with this project, you can clone the repository and follow the instructions in the `README.md` files located in each folder. The `data_collection` folder contains detailed steps to set up and run the Arduino and Python scripts for data collection. The `analysis` folder contains Jupyter notebooks for the data analysis process.

## Conclusion

This project aims to provide a systematic approach to characterizing ultrasonic sensors, addressing the challenges faced by students in the MIE 444 course. By automating data collection and applying advanced analytical techniques, we hope to improve the reliability and performance of sensors used in autonomous cars. The findings from this project can also benefit manufacturing companies like Magna, enhancing the quality and performance of sensors used in their autonomous vehicle applications.

For any questions or contributions, feel free to open an issue or submit a pull request.

---

### Table of Contents

1. [Motivation](#motivation)
2. [Project Overview](#project-overview)
3. [Repository Contents](#repository-contents)
4. [Getting Started](#getting-started)
5. [Conclusion](#conclusion)

---

Feel free to reach out if you have any questions or need further assistance!
