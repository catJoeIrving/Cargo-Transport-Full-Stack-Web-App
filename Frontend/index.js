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

app.get('/home',function (req, res) {
  res.render('pages/home')
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
          res.render('pages/home')
        }
      })
      .catch((error) => {
        console.log(error)
      });
});

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

// Page for all spaceship records
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
app.get('/addSpaceship',messages,function (req, res) 
{
    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/addSpaceship', { data: userData });
      });
});

app.post('/addSpaceship',function (req, res) 
{
    var spaceshipid = req.body.spaceshipid;
    var maxweight = req.body.maxweight;
    var captainid = req.body.captainid;
    console.log(captainid);

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

    var message = "Spaceship successfully added!";
    res.locals.message = message;

    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/addSpaceship', { data: userData });
    });
});

// Page to update a spaceship
app.get('/updateSpaceship',messages,function (req, res) 
{
    axios.get('http://127.0.0.1:5000/api/captain/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/updateSpaceship', { data: userData });
      });
});


app.post('/updateSpaceship',function (req, res) 
{

    var spaceshipid = req.body.spaceshipid;
    var maxweight = req.body.maxweight;
    var captainid = req.body.captainid;

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

    var message = "Spaceship successfully updated!";
    res.locals.message = message;

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

    var message = "Spaceship successfully deleted!";
    res.locals.message = message;

    res.render('pages/removeSpaceship');
});

app.get('/addCargo',messages,function (req, res) 
{
  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/addCargo', { data: userData });
    });
});


app.post('/addCargo',function (req, res) 
{
  var cargoid = req.body.cargoid;
  var weight = req.body.weight;
  var cargotype = req.body.cargotype;
  var spaceship = req.body.spaceship;

  
  axios.post('http://127.0.0.1:5000/api/cargo', {
      secondary_id: cargoid,
      weight: weight,
      cargotype: cargotype,
      secondary_ship_id: spaceship
    })
    .then(function (response) {
      console.log(response);
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

  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/addCargo', { data: userData });
    });
});

app.get('/updateCargo',messages,function (req, res) {
  axios.get('http://127.0.0.1:5000/api/spaceship/all')
    .then(response => {
      let userData = response.data;
      console.log(userData);
      res.render('pages/updateCargo', { data: userData });
    });
});


app.post('/updateCargo',function (req, res) 
{
  var cargoid = req.body.cargoid;
  var weight = req.body.weight;
  var cargotype = req.body.cargotype;
  var spaceship = req.body.spaceship;
  var departure = req.body.departure;
  var arrival = req.body.arrival;
  console.log(cargotype, departure, arrival, arrival)

  
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