const express = require('express')
var path = require('path');
var bodyParser = require('body-parser');
const axios = require('axios'); // import the axios module
const app = express();
const port = 3000;
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
//setup public folder
app.use(express.static('./public'));
// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));
// parse application/json
app.use(bodyParser.json());

//our alert message midleware
function messages(req,res,next){
    var message;
    res.locals.message = message;
    next();
}

app.get('/',function (req, res) {
  res.render('pages/login')
});

app.get('/login', function (req, res) {
  var login = 'http://127.0.0.1:5000/api/login'
  var username = req.query.username; 
  var password = req.query.password;
  let config = 
  {
    headers: 
    {
      username: username,
      password: password
    }
  }

  axios.get(login, config)
      .then((response)=> {
        let apiResponse = response.data
        console.log('username:', username);
        console.log('password:', password);
        if (apiResponse == 'False')
        {
          res.render('pages/loginUnsuccessful', 
          {
            message: 'Login unsuccessful'
            
          });
        } 
        else        
        {
          axios.get('http://127.0.0.1:5000/api/cargo/all')
            .then(response => {
            let userData = response.data;
            console.log(userData);
            res.render('pages/cargoEnRoute', { data: userData });
          });
        }
      })
      .catch((error) => {
        console.log(error)
      });
});


// Cargo pages
// Worked on by Joseph Irving

// These three do the same thing, each gets the records from the cargo/all API so the page can loop through them to load as appropriate for that page
app.get('/cargo', function(req, res) 
{
    axios.get('http://127.0.0.1:5000/api/cargo/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/cargoAll', { data: userData });
      });
});

  app.get('/cargoArrived', function(req, res) 
  {
    axios.get('http://127.0.0.1:5000/api/cargo/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/cargoArrived', { data: userData });
      });
  });

  app.get('/cargoEnRoute', function(req, res) 
  {
    axios.get('http://127.0.0.1:5000/api/cargo/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/cargoEnRoute', { data: userData });
      });
  }); 
      
// Spachship Table Page
// Worked on by Joseph Irving

// Page for all spaceship records, grabs all records from the spaceship/all api and loads the page with it
app.get('/spaceship', function(req, res) 
{
    axios.get('http://127.0.0.1:5000/api/spaceship/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/spaceship', { data: userData });
      });
  });

// Page to add a spaceship
// This gets all captains from captain table so the addSpaceship page can load with a drop down selection of available captains
app.get('/addSpaceship',messages,function (req, res) 
{
    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/addSpaceship', { data: userData });
      });
});

// POST version of the add spaceship page to send the information to the POST api on the back end to make a new spaceship in the DB
app.post('/addSpaceship',function (req, res) 
// Get the variables from the body and assign them
{
    var spaceshipid = req.body.spaceshipid;
    var maxweight = req.body.maxweight;
    var captainid = req.body.captainid;
    console.log(captainid);
// Call the post API with the variables from the body
    axios.post('http://127.0.0.1:5000/api/spaceship', {
        secondary_id: spaceshipid,
        maxweight: maxweight,
        captainid: captainid
      })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });
// Success message to be shown after submission
    var message = "Spaceship successfully added!";
    res.locals.message = message;
// Calls captain/all API again so the page can again load with captains drop down for a new POST
    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/addSpaceship', { data: userData });
    });
});

// Page to update a spaceship
// This gets all captains from captain table so the updateSpaceship page can load with a drop down selection of available captains

app.get('/updateSpaceship',messages,function (req, res) 
{
    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/updateSpaceship', { data: userData });
      });
});

// POST version of updateSpaceship page
app.post('/updateSpaceship',function (req, res) 
{
// Assign variables from body
    var spaceshipid = req.body.spaceshipid;
    var maxweight = req.body.maxweight;
    var captainid = req.body.captainid;
// Send variables to PUT API 
    axios.put('http://127.0.0.1:5000/api/spaceship', {
        secondary_id: spaceshipid,
        maxweight: maxweight,
        captainid: captainid
      })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });
// Success message upon submission
    var message = "Spaceship successfully updated!";
    res.locals.message = message;
// Get captains again for dropdown selection
    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/updateSpaceship', { data: userData });
    });
});


// To remove a Spaceship
app.get('/removeSpaceship',function (req, res) 
{
    res.render('pages/removeSpaceship')
});

// Gets spaceship ID from body, calls DELETE api for spaceship and sends it the information from body
app.post('/removeSpaceship', function (req, res) 
{
    var spaceshipid = req.body.spaceshipid;

    axios.delete('http://127.0.0.1:5000/api/spaceship', {
        data: {
            secondary_id: spaceshipid // This was throwing errors, ChatGPT said wrap it in data: {} because DELETE takes different parameters
            // than POST and PUT
        }
    })
    .then(function (response) {
        console.log(response);
    })
    .catch(function (error) {
        console.log(error);
    });
// Success message on submission
    var message = "Spaceship successfully deleted!";
    res.locals.message = message;

    res.render('pages/removeSpaceship');
});

// Gets spaceship records to load as drop down selection for add cargo page
app.get('/addCargo',messages,function (req, res) 
{
  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/addCargo', { data: userData });
    });
});

// POST version of addCargo, first get variables from the body and assign them
app.post('/addCargo',function (req, res) 
{
  var cargoid = req.body.cargoid;
  var weight = req.body.weight;
  var cargotype = req.body.cargotype;
  var spaceship = req.body.spaceship;

  // send variables to cargo POST API
  axios.post('http://127.0.0.1:5000/api/cargo', {
      secondary_id: cargoid,
      weight: weight,
      cargotype: cargotype,
      secondary_ship_id: spaceship
    })
    .then(function (response) {
      console.log(response);
      // backend API returns custom error messages if there's a problem, otherwise returns success message for the user
      if (response.data === true) {
        var message = "Cargo successfully added!";
      }
      else {
        var message = response.data;
      }
      res.locals.message = message;
    })
    .catch(function (error) {
      console.log(error);
    });

    // gets all spaceship records to load the addCargo page with a drop down selector for spaceships
  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/addCargo', { data: userData });
    });
});

    // gets all spaceship records to load the updateCargo page with a drop down selector for spaceships
app.get('/updateCargo',messages,function (req, res) {
  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/updateCargo', { data: userData });
    });
});

// POST version of update cargo page, first gets variables from the body
app.post('/updateCargo',function (req, res) 
{
  var cargoid = req.body.cargoid;
  var weight = req.body.weight;
  var cargotype = req.body.cargotype;
  var spaceship = req.body.spaceship;
  var departure = req.body.departure;
  var arrival = req.body.arrival;
  console.log(cargotype, departure, arrival, arrival)

// sends the user entered variables to the cargo PUT API  
  axios.put('http://127.0.0.1:5000/api/cargo', {
      secondary_id: cargoid,
      weight: weight,
      cargotype: cargotype,
      secondary_ship_id: spaceship,
      departure: departure,
      arrival: arrival
    })
    .then(function (response) {
      console.log(response);
      // backend API returns custom error messages if there's a problem, otherwise returns success message for the user
      if (response.data === true) {
        var message = "Cargo successfully updated!";
      }
      else {
        var message = response.data;
      }
      res.locals.message = message;
    })
    .catch(function (error) {
      console.log(error);
    });

    // gets all spaceship records to load updateCargo page with a dropdown selection for spaceships
  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/updateCargo', { data: userData });
    });
});

// To remove a Cargo record
app.get('/removeCargo',function (req, res) 
{
  res.render('pages/removeCargo')
});

// POST version of /removeCargo that takes the information the user entered and sends it to the cargo DELETE api
app.post('/removeCargo', function (req, res) 
{
  var cargoid = req.body.cargoid;

  axios.delete('http://127.0.0.1:5000/api/cargo', {
      data: {
        secondary_id: cargoid
      }
  })
  .then(function (response) {
      console.log(response);
  })
  .catch(function (error) {
      console.log(error);
  });
// returns success message on submit
  var message = "Cargo successfully deleted!";
  res.locals.message = message;

  res.render('pages/removeCargo');
});

// Page to render Captain page 
// Worked on by Becky Tseng 

// Captain page to show all captains 
app.get('/captain', function(req, res) 
{
  axios.get('http://127.0.0.1:5000/api/captain/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/captainAll', { data: userData });
    });
});



app.get('/addCaptain',messages,function (req, res) 
{
  axios.get('http://127.0.0.1:5000/api/captain/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/addCaptain', { data: userData });
    });
});

// Adding a captain 

app.post('/addCaptain',function (req, res) 
{
    var secondary_id = req.body.secondary_id;
    var firstname = req.body.firstname;
    var lastname = req.body.lastname;
    var rank = req.body.rank;
    var homeplanet = req.body.homeplanet;

    axios.post('http://127.0.0.1:5000/api/captain', {
        secondary_id: secondary_id,
        firstname: firstname,
        lastname: lastname,
        rank: rank,
        homeplanet: homeplanet
      })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });

    var message = "Captain successfully added!";
    res.locals.message = message;

    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/addCaptain', { data: userData });
    });
});


// Update captain information 

app.get('/updateCaptain',messages,function (req, res) {
  axios.get('http://127.0.0.1:5000/api/captain/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/updateCaptain', { data: userData });
    });
});


app.post('/updateCaptain',function (req, res) {
  var captainid = req.body.captainid;
  var firstname = req.body.firstname;
  var lastname = req.body.lastname;
  var rank = req.body.rank;
  var homeplanet = req.body.homeplanet;
  console.log(captainid, firstname, lastname, rank, homeplanet)

  
  axios.put('http://127.0.0.1:5000/api/captain', {
      secondary_id: captainid,
      firstname: firstname,
      lastname: lastname,
      rank: rank,
      homeplanet: homeplanet,
    })
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    });

    var message = "Captain successfully updated!";
    res.locals.message = message;

  axios.get('http://127.0.0.1:5000/api/captain/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/updateCaptain', { data: userData });
    });
});

// Remove captain

app.get('/removeCaptain',function (req, res) {
  res.render('pages/removeCaptain')
});

app.post('/removeCaptain', function (req, res) {
  var captainid = req.body.captainid;

  axios.delete('http://127.0.0.1:5000/api/captain', {
      data: 
      {
        secondary_id: captainid
      }
  })
  .then(function (response) {
      console.log(response);
  })
  .catch(function (error) {
      console.log(error);
  });

  var message = "Captain successfully deleted!";
  res.locals.message = message;

  res.render('pages/removeCaptain');
});


app.listen(port, () => console.log(`MasterEJS app Started on port ${port}!`));

// References:
// ChatGPT
// Green template example from class
// https://axios-http.com/docs/post_example
//