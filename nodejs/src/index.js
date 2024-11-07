const express = require("express");
const bodyParser = require("body-parser");
const morgan = require("morgan");
const fs = require("fs");
const util = require("util");
const path = require("path");

const port = parseInt(process.env.PORT, 10) || 3000;

const app = express();

// body parser
app.use(bodyParser.urlencoded({ extended: true }));

// set the view engine to ejs
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "/views"));

const access = fs.createWriteStream(path.join(__dirname, "./output.log"), {
  flags: "w",
});

console.log = function (d) {
  //
  access.write(util.format(d) + "\n");
};

const logFile = fs.createWriteStream(path.join(__dirname, "./acces.log"), {
  flags: "a",
});
app.use(morgan({ stream: logFile }));

/* Postgres DB Connection. Follow the documentation: https://node-postgres.com */
const { Client } = require("pg");

const DB_CONNECTION = {
  user: "ddss-database-assignment-2",
  database: "ddss-database-assignment-2",
  password: "ddss-database-assignment-2",
  host: process.env.DB_HOST || "localhost",
  port: 5432,
};

const client = new Client(DB_CONNECTION);
client.connect();

const printQueryResultsWithTitle = (title) => (err, res) => {
  if (err) {
    console.log(err.stack);
  } else {
    console.log(title);
    console.log(res.rows);
  }
};

client.query(
  "SELECT * from messages",
  printQueryResultsWithTitle("\n\n == Messages Contents == \n")
);
client.query(
  "SELECT * from books",
  printQueryResultsWithTitle("\n\n == Books Contents == \n")
);

/* Web server configurations to receive requests */
app.get("/", async (req, res) => {
  res.render("pages/index");
});

app.get("/part1", (req, res) => {
  res.render("pages/part1");
});

app.get("/part1_vulnerable", (req, res) => {
  res.render("pages/part1_vulnerable_results", { ...req.query });
});

app.get("/part1_correct", (req, res) => {
  res.render("pages/part1_correct_results", { ...req.query });
});

app.get("/part2", (req, res) => {
  res.render("pages/part2");
});

app.get("/part3", (req, res) => {
  res.render("pages/part3");
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`));
