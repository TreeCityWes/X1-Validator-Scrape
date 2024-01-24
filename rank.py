name: Python application

on:
  schedule:
    - cron: '*/10 * * * *'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'  # Adjust to your Python version

    - name: Install Chrome
      run: |
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable

    - name: Install Chrome WebDriver
      run: |
        CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
        DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
        wget -q "https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip"
        unzip chromedriver_linux64.zip
        sudo mv chromedriver /usr/bin/chromedriver
        sudo chmod +x /usr/bin/chromedriver

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install selenium

    - name: Run script
      run: python rank.py

    - name: Commit files
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -f *.csv
        git commit -m "Add generated CSV files" -a || echo "No changes to commit"
        git push
      env:
        GITHUB_TOKEN: ${{ secrets.Validator }}
