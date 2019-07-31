const express = require('express')
const app = express()
const port = 3000
const path = require('path')
const csvFilePath = 'merge_data.csv'
const csvFilePath2 = 'prediction.csv'
const csv = require('csvtojson')
app.use(express.static('./'))

app.get('/fetch-predicted-price', function (req, res) {
    csv()
        .fromFile(csvFilePath2)
        .then((jsonObj) => {
            var dates = jsonObj[jsonObj.length - 1].Time.split('-');
            var dateString = "20"+dates[0]+"-"+dates[1]+"-"+dates[2] + " " + dates[3]+":"+dates[4]+":00.000";
            var unixTimestamp = Math.round(new Date(dateString).getTime());  
        res.json({ Prediction: jsonObj[jsonObj.length - 1].Prediction, Time: unixTimestamp });
        });
})

app.get('/fetch-btc-price', function (req, res) {
    csv()
        .fromFile(csvFilePath)
        .then((jsonObj) => {
            res.json({ Price: jsonObj[jsonObj.length - 1].Price, Sentiment: jsonObj[jsonObj.length - 1].Sentiment });
        });
})

app.get('/plot-graph-price', function (req, res) {
    //console.log(Date.now());
    csv()
        .fromFile(csvFilePath)
        .then((jsonObj) => {
            var actual = [];
            var predicted = [];
            jsonObj.forEach(obj => {
                var dates = obj.Time.split('-');
                var dateString = "20"+dates[0]+"-"+dates[1]+"-"+dates[2] + " " + dates[3]+":"+dates[4]+":00.000";
                var unixTimestamp = Math.round(new Date(dateString).getTime());
                actual.push({t: unixTimestamp, y: obj.Price})
                predicted.push({t: unixTimestamp, y: obj.Prediction})
            })
            res.json({ actual: actual, predicted: predicted });
        });
})

app.get('/model-accuracy', function (req, res) {
    //console.log(Date.now());
    csv()
        .fromFile(csvFilePath)
        .then((jsonObj) => {
            var trueTrend= 0;
            for(var i=1 ; i<jsonObj.length ; i++) {
                if (((jsonObj[i].Prediction-jsonObj[i-1].Prediction)<=0 && (jsonObj[i].Price - jsonObj[i-1].Price)<=0) || ((jsonObj[i].Prediction-jsonObj[i-1].Prediction) >= 0 && (jsonObj[i].Price - jsonObj[i-1].Price)>=0))
                    trueTrend++;
            }
            var count = jsonObj.length - 1;
            var accuracy = (trueTrend / count) * 100;

            res.json({ accuracy: accuracy });
        });
})

app.get('/plot-graph-sentiment', function (req, res) {
    //console.log(Date.now());
    csv()
        .fromFile(csvFilePath)
        .then((jsonObj) => {
            var sentiment = [];
            jsonObj.forEach(obj => {
                var dates = obj.Time.split('-');
                var dateString = "20"+dates[0]+"-"+dates[1]+"-"+dates[2] + " " + dates[3]+":"+dates[4]+":00.000";
                var unixTimestamp = Math.round(new Date(dateString).getTime());
                sentiment.push({t: unixTimestamp, y: obj.Sentiment})
            })
            res.json({ sentiment: sentiment });
        });
})

app.get('/plot-graph-sentiment', function (req, res) {
    //console.log(Date.now());
    csv()
        .fromFile(csvFilePath)
        .then((jsonObj) => {
            var sentiment = [];
            jsonObj.forEach(obj => {
                var dates = obj.Time.split('-');
                var dateString = "20"+dates[0]+"-"+dates[1]+"-"+dates[2] + " " + dates[3]+":"+dates[4]+":00.000";
                var unixTimestamp = Math.round(new Date(dateString).getTime());
                sentiment.push({t: unixTimestamp, y: obj.Sentiment})
            })
            res.json({ sentiment: sentiment });
        });
})

app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname + '/index.html'));
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))