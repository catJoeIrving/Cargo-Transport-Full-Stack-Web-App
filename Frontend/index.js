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

app.get('/',function (req, res) {
    res.render('pages/home')
});

app.get('/links',function (req, res) {
    //array with items to send
    var items = [
        {name:'node.js',url:'https://nodejs.org/en/'},
        {name:'ejs',url:'https://ejs.co'},
        {name:'expressjs',url:'https://expressjs.com'},
        {name:'vuejs',url:'https://vuejs.org'},
        {name:'nextjs',url:'https://nextjs.org'}];

    res.render('pages/links',{
        links:items
    })
});

app.get('/list',function (req, res) {
    //array with items to send
    var items = ['node.js','expressjs','ejs','javascript','bootstarp'];
    res.render('pages/list',{
        list:items
    })
});

app.get('/cargo', function(req, res) {
    axios.get('http://127.0.0.1:5000/api/cargo/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/cargoAll', { data: userData });
      });
  });

  app.get('/cargoArrived', function(req, res) {
    axios.get('http://127.0.0.1:5000/api/cargo/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/cargoArrived', { data: userData });
      });
  });

  app.get('/cargoEnRoute', function(req, res) {
    axios.get('http://127.0.0.1:5000/api/cargo/all')
      .then(response => {
        let userData = response.data;
        console.log(userData);
        res.render('pages/cargoEnRoute', { data: userData });
      });
  });
       

//our alert message midleware
function messages(req,res,next){
    var message;
    res.locals.message = message;
    next();
}

app.get('/form',messages,function (req, res) {
    res.render('pages/form');
});

app.post('/form',function (req, res) {
    var message=req.body;
    res.locals.message = message;
    res.render('pages/form');
});

app.listen(port, () => console.log(`MasterEJS app Started on port ${port}!`));