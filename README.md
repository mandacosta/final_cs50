# Final Project - CS50🏁
Final project for the CS50's course

## 🎁 Secret Santa !
#### Video Demo:  https://www.youtube.com/watch?v=BUGKOqmBeXQ
#### Description:
Welcome to our web application, designed to facilitate the seamless creation of Secret Santa groups with your friends! With our platform, you can effortlessly set up a group, outlining its purpose, and even list your gift preferences for your Secret Santa to ensure a perfect surprise. As a group owner, you have full control, allowing you to draw the Secret Santa assignments, manage group members, and even delete the group itself. Start spreading the holiday joy and make your Secret Santa experience memorable with our user-friendly application!
Have fun 💙

#### Files Structure:
Source:
  - app.py: This file serves as the core of our web application, housing the Flask framework and its corresponding routes, responsible for handling user requests and rendering appropriate responses.
  - helpers.py: Within this file, you'll find a 'login_required' decorator, which defines the routes requiring user authentication. It also includes 'format_list_of_groups' to efficiently organize lists of members and pertinent information, such as user ownership status.
  - db_creation: This module contains SQL queries essential for creating and initializing the database that our application relies on.
  - database.db: This is the actual database file, housing all the structured data necessary for the application's functionality. It can be explored and manipulated using a compatible tool, such as a Visual Studio Code extension like SQLite Viewer.

Templates:
  - This directory contains a collection of HTML files. These templates are responsible for generating the various pages presented to the user.

Static:
  - css: The cascading style sheets (CSS) are responsible for the design, layout, and overall aesthetics of the application.
  - script: JavaScript functions that enhance the interactivity and dynamism of our web application
  - images:  Here, you can find a collection of .jpeg files used within the application to enhance the visual elements and user experience.

#### Main Techs
- Python and Flask
- sqlite and SQL
- HTML, Jinja, CSS and JavaScript
- Bootstrap
- Pictures from: https://www.shutterstock.com/pt/search/no-results-icon
