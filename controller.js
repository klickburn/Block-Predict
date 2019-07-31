var app = angular.module('myApp', []);
                                        app.controller('myCtrl', function ($scope, $http, $interval) {
                                            fetchBTCPrice();
                                            modelAccuracy();
                                            fetchPredictedPrice();
                                            plotGraph();
                                            fetchCurrentTime();
                                            
                                            $interval(fetchBTCPrice, 5000);
                                            $interval(modelAccuracy, 5000);
                                            $interval(fetchPredictedPrice, 5000);
                                            $interval(plotGraph, 10000);
                                            $interval(fetchCurrentTime, 1000);
                                            
                                            function fetchCurrentTime() {
                                                 $scope.currentTime = new Date();
                                            }
                                           
                                            
                                            function fetchBTCPrice() {
                                                $http({
                                                method: 'GET',
                                                url: '/fetch-btc-price'
                                            }).then(function (results) {
                                                $scope.btcPrice = results.data.Price;
                                                $scope.sentiment = results.data.Sentiment;
                                                //console.log($scope.btcPrice, $scope.sentiment);
                                            })
                                            }
                                            
                                            function modelAccuracy() {
                                                 $http({
                                                method: 'GET',
                                                url: '/model-accuracy'
                                            }).then(function (results) {
                                                $scope.accuracy = results.data.accuracy;
                                                //console.log($scope.btcPrice, $scope.sentiment);
                                            })
                                            }
                                           
                                            function fetchPredictedPrice() {
                                                $http({
                                                method: 'GET',
                                                url: '/fetch-predicted-price'
                                            }).then(function (results) {
                                                $scope.futureTime = results.data.Time;
                                                $scope.Prediction = results.data.Prediction;
                                                //console.log($scope.btcPrice, $scope.sentiment);
                                            })
                                            }
                                            
                                            
                                            function plotGraph() {
                                                $http({
                                                method: 'GET',
                                                url: '/plot-graph-price'
                                            }).then(function (results) {
                                                console.log(results.data);
                                                var data = results.data.actual;
                                                var data2 = results.data.predicted;
                                                var ctx = document.getElementById('chart1').getContext('2d');
                                                ctx.canvas.width = 1300;
                                                ctx.canvas.height = 500;

                                                var color = Chart.helpers.color;
                                                var cfg = {
                                                    type: 'line',
                                                    data: {
                                                        datasets: [{
                                                            label: 'Actual BTC Price',
                                                            backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
                                                            borderColor: window.chartColors.red,
                                                            data: data,
                                                            type: 'line',
                                                            pointRadius: 0,
                                                            fill: false,
                                                            lineTension: 0,
                                                            borderWidth: 1
                                                        },
                                                        {
                                                            label: 'Predicted BTC Price',
                                                            backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
                                                            borderColor: window.chartColors.blue,
                                                            data: data2,
                                                            type: 'line',
                                                            pointRadius: 0,
                                                            fill: false,
                                                            lineTension: 0,
                                                            borderWidth: 1
                                                        }]
                                                    },
                                                    options: {
                                                        scales: {
                                                            xAxes: [{
                                                                type: 'time',
                                                                distribution: 'series',
                                                                ticks: {
                                                                    source: 'auto',
                                                                    autoSkip: true
                                                                }
                                                            }],
                                                            yAxes: [{
                                                                scaleLabel: {
                                                                    display: true,
                                                                    labelString: 'BTC price ($)'
                                                                }
                                                            }]
                                                        },
                                                        tooltips: {
                                                            intersect: false,
                                                            mode: 'index',
                                                            callbacks: {
                                                                label: function (tooltipItem, myData) {
                                                                    //console.log(tooltipItem);
                                                                    //console.log(myData);
                                                                    var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                                                                    if (label) {
                                                                        label += ': ';
                                                                    }
                                                                    label += parseFloat(tooltipItem.yLabel).toFixed(2);
                                                                    return label;
                                                                }
                                                            }
                                                        }
                                                    }
                                                };

                                                var chart = new Chart(ctx, cfg);
                                            })
                                            }

                                        });