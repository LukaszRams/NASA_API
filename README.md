# NASA Api for wallpapers

An application using the **EPIC DAILY "BLUE MARBLE" API** to download images of the earth, edit them 
and set them as a desktop background.

The application is equipped with automatic detection of incorrect files in the source folder, deleting them 
and if new data is available updating.


***Application created for educational purposes only***   

##### Thanks to <a href="https://epic.gsfc.nasa.gov/about/api" target="_blank">EPIC DAILY "BLUE MARBLE" API</a>


## Instruction

### Development
1. Use Poetry to create virtual environment and install dependencies
```commandline
make setup
```

2. Run code
```commandline
make run
```

### Building

2. Build your application

Simply call

```commandline
make build
```

### Launching

Go to the ***nasaApi*** folder and double-click on ***NASA_Api.exe***

*If you want the application to run automatically on startup, add it to autostart*
