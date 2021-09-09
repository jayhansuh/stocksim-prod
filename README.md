# stocksim-prod
VR based stock social networking service - stocksim.net

# Set up and the first run
1. Fork this repository (Button on right top of the page https://github.com/hansuh/stocksim-prod)
2. Clone the forked repository (git clone https://github.com/... on your computer)
3. Add existing local repository on Sourcetree
4. Switch to dev-local branch of the git (git checkout dev-local)
6. Make or download a local database file
7. Run db job scheduler (python manage.py shell < sch.py)
To run it in background
python manage.py shell < sch.py &
kill [PID]
8. Run server (python manage.py runserver)

# Workflow
1. Pull any updates from source tree or git command
2. Modify code and test on your local database
3. Run test pipeline
4. Commit & push your changes on Sourcetree(pull & merge first if sourcetree ask you to do)
5. Create a pull request

# Useful Links

## Django tutorial & docs
https://docs.djangoproject.com/en/3.2/intro/tutorial01/

## Dream coding
Git
https://youtube.com/playlist?list=PLv2d7VI9OotQUUsgcTBHuy5vJkSgzVHL0

JS
https://youtube.com/playlist?list=PLv2d7VI9OotTVOL4QmPfvJWPJvkmv6h-2

VS code
https://youtu.be/EVxCdenPbFs
https://youtu.be/bS9yTI2fC0w

CSS flexbox
https://youtu.be/7neASrWEFEM
https://css-tricks.com/snippets/css/a-guide-to-flexbox/


# To Do v1

(*) are milestone markings for the first release version

## How To pages

1. Add graphics to the How-To pages for Main, Swing trade game (*)

2. Mobile version How-To (*)

## Browser localstorage

1. ~~Add date marking to call clearLocalDB function~~ (HGS)

## Main page & Table UI

1. Add page numbers to transaction or memo lists (*)

2. ~~Replace ticker name by today's change and MA25 number~~ (JYL)\

2.1 ~~Update localdb for today's change of tickers~~ (HGS)

3. Add stocksim index line

4. Use d3.js for main page chart (*)

5. number of asset lines based on follower list (JYL)

6. Discontinous animation during entry mode scroll (*)

## Database & Server hosting

1. Migrate server hosting service to Azure from pythonanywhere (HGS)\

1.1 ~~Set up B1 service plan and PostgreSQL~~

1.2 Import previous data from pythonanywhere

2. Redesign job scheduler (HGS)

3. Yf bulk download

4. Marking tickers and players needed to be updated

5. International stocks(Mainly Korea and European countries not listed on Yahoo finance)

6. Dividend update

## Agora/Portfolio model (JYL)

1. follower list (*)

2. favorite tickers (*)

3. Show filtered player list in the main page (*)

4. Agora configuration based on follower or ticker list (*)

5. Add news article link and headline for tickers (*)

6. Add Q&A board for portfolio review (*)

7. Share function - embedded html image with stocksim.net link, or png download

## Registration

1. SNS login system (*)

2. Referral code system (*)

## Etc

1. Quant Lab

2. Test pipeline and CI autotest

3. Build a basic VR by using three.js like https://www.cryptovoxels.com/

4. Npm parcel and source code minimization or js obfuscation

5. Language preference(eng default) and auto translation

6. Azonix font to special letters and Korean letters

7. Mobile app

8. License and terms of use / about us page (*)
