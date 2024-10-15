# **Live-Video-Tracking**: <br> Video analysis solution and athletes' tracking, applied to rugby

## **Problem:**

Artificial intelligence is becoming increasingly prevalent in all areas of life, particularly in sports. Many companies are now seeking to innovate by creating projects that combine AI and data analytics. Our goal is to contribute to this growing field by offering an innovative video analysis solution, specifically tailored for rugby.

Currently, despite significant advancements in sports data analytics, no available solution provides comprehensive video analysis and player tracking using image processing in rugby.

## **Objectives:**

The objectives of this project are to:

- Develop algorithms to recognize players regardless of the camera angle
- Implement modules for tracking and highlighting players on screen
- Incorporate features for generating real-time and historical statistics on matches, teams, and players

## **Final Goal:**

We aim to develop a tool that allows real-time tracking of targets in video streams (live feed or slightly delayed). This technology will be applied to rugby, enabling users to track players, referees, the ball, and more, allowing full customization of what they see.

**Visually**:  
- Similar to the Canal+ Expert Mode.

**Technically**:  
- A web-based application
- Player recognition algorithms
- Selection panel for tracking specific players

## **Technologies & Tools:**

- **Current tools**: We are primarily using **OpenCV** for image processing, but we remain open to integrating more efficient models if needed.
- **Programming language**: The project is being developed in **Python**, allowing flexibility for future developments. For the web application, we plan to use **Flask** for the backend, with potential integration of **React** for a more visually dynamic interface.
- **Machine learning models**: Our approach will involve pre-built models for object detection and player recognition, but we will fine-tune and train these models with our custom datasets to closely align with our specific needs.
- **Data acquisition**: We plan to use web scraping to build our dataset, giving us the ability to label and organize our data in a way that optimally serves the project's goals.

## **Challenges & Constraints:**

Several challenges are expected during the project’s development, including:

- **Camera distance**: Players will often appear small or blurry when cameras are far from the action.
- **Player movement**: Fast movements, changes in direction, and frequent occlusions (e.g., players blocking others) could make tracking difficult.
- **Obscured faces**: Players are often viewed from behind or in profile, which limits facial recognition.
- **Computational power**: We have yet to assess the exact computing resources required, but we may explore cloud-based solutions for training the models and handling real-time video processing.

## **Features & Functionalities:**

### **Phase 1: Initial Research and Development**
1. **Researching models**: We will first explore models that best fit our study, with a focus on player recognition in dynamic environments.
2. **Developing the recognition algorithm**:
    - **Face detection**
    - **Jersey number detection**
    - **Player database creation**: Through web scraping and manual data entry
    - **Linking faces to the player database**
    - **Player tracking via memory and prediction mechanisms**
    - ***Bonus***: Detecting players by their gait or body type (if applicable in the future)
3. **Creating a user interface**:
    - Video insertion and processing
    - Features and parameters for video analysis
4. **Selecting players to follow**:
    - Ability to select one or multiple players via filters and search tools
    - Target highlighting for selected players

### **Phase 2: Ball Possession Tracking**
1. **Tracking ball possession**:
    - Identifying the ball’s location in the video
    - Recognizing the player closest to the ball
2. ***Bonus***: Providing statistics related to ball possession (e.g., time of possession, meters covered).

### **Phase 3: Action Detection**
1. **Recognizing game events**:
    - Detecting tackles, passes, and forward passes through machine learning.

### **Phase 4: Strategy Proposal**
1. **AI-driven strategy recommendations**:
    - Detecting weaknesses in gameplay
    - Suggesting strategies based on the detected data

## **Statistics & User Interface**

As the project progresses, we aim to improve the web application’s **user experience** (UX) and **ergonomics**. The interface will allow users to visualize a wealth of useful statistics in real time and from past games. Planned features include:

- **Historical data**: Statistics on players from past matches, such as total games played, average performance metrics, etc.
- **Real-time statistics**: Data such as time spent in play, distance covered during the game, possession percentage, and more.

## **Next Steps:**
As we continue developing the project, future tasks will involve:
1. Improving player recognition algorithms based on the challenges posed by camera angles and occlusions.
2. Refining the web application interface with React or Flask.
3. Scaling the project to handle large datasets and real-time video streams.
4. Optimizing computational resources, potentially exploring cloud computing solutions for efficient model training and deployment.
