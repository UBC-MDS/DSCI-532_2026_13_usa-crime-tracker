# Contributing to Our Project

This document outlines the process to propose a change to our crime analysis dashboard project. 

## Fixing Typos
Small typos or grammatical errors in documentation may be edited directly using the GitHub web interface, so long as the changes are made in the source file.
- YES: you edit a roxygen comment in a .R file below R/.
- NO: you edit an .Rd file below man/.

## Prerequisites
- Before you make a substantial pull request, you should always file an issue and make sure someone from the team agrees that it's a problem. If you've found a bug, create an associated issue and illustrate the bug with a minimal [reprex](https://tidyverse.org/help/#reprex). 

## Pull Request process
- it is reccomended to use a Git Branch for each pull request
- New code should follow the tidyverse [style guide](https://style.tidyverse.org/) or PEP8 [style guide](https://peps.python.org/pep-0008/).

## Code of Conduct
- This project is released with a Contributor Code of Conduct (located in the repo). By participating in this project you agree to abide by its terms.

### M3 Collaboration Retrospective

**M3 review:**

After Ilya's suggestions and mid-M3 reviews, we made a commitment to reviewing all PR's and ensuring no self-merging or merging directly to main, as these were some of our larger issues. The team did well with this as everyone made a strong commitment to ensure this was upheld. Ilya also suggested that we update our workflow to remove larger PR's with lots of code to break down the work of reviewers. This happened a few times, where large commits were merged without proper review. The last remaining issue noted was the spreading of contributions among team members. The code base was largely dominated by a few members, somewhat due to the implementations of charts which required more code, but also due to mismanagement of tasks. Some other issues we had were descriptive PR comments, clear assignment of tasks, and last minute work rushes.


**M4 commitments:**
Moving into M4 made a commitment to ensure continued review PR's, and added commitments to make more description to PR messages, create a clearer assigment of responsibilites, and better distribute workload across members. To this end we decided to create a reviewer role for M4. This persons job is to handle all project management aspects of the milestones - creation and distribution of tasks as issues, PR reviewing, and complete any written components. This role was given to the person with the largest current contribution to the codebase. This will ideally ensure proper workflows are followed, and management of work is well balanced. Lastly, we wanted to avoid last minute deadlines this milestone. As such, we have commited to soft deadline for work of friday night, and a hard deadline for sunday night. Ideally, all team memebers should have initial commits completed by Friday, and PR's commited by sunday night. This will give us time to review any PR's and make subsequent changes over Monday and Tuesday as needed.

## Attribution
These contributing guidelines were adapted from the [dplyr contributing guidelines](https://github.com/tidyverse/dplyr/blob/main/.github/CONTRIBUTING.md) as well as Tiffany Timbers ["Contributing to the Breast Cancer Predictor project"](https://github.com/ttimbers/breast-cancer-predictor/blob/0.0.1/CONTRIBUTING.md) file.
