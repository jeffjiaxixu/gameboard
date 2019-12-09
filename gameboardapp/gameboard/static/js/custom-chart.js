//https://stackoverflow.com/questions/1293147/javascript-code-to-parse-csv-data
function CSVToArray( strData, strDelimiter ){
    strDelimiter = (strDelimiter || ",");

    var objPattern = new RegExp(
        (
            "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +
            "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +
            "([^\"\\" + strDelimiter + "\\r\\n]*))"
        ),
        "gi"
    );

    var arrData = [[]];
    var arrMatches = null;

    while (arrMatches = objPattern.exec( strData )){
        var strMatchedDelimiter = arrMatches[ 1 ];

        if (
            strMatchedDelimiter.length &&
            strMatchedDelimiter !== strDelimiter
        ){
            arrData.push( [] );
        }

        var strMatchedValue;
        if (arrMatches[ 2 ]){

            strMatchedValue = arrMatches[ 2 ].replace(
                new RegExp( "\"\"", "g" ),
                "\""
            );
        } else {
            strMatchedValue = arrMatches[ 3 ];
        }
        arrData[ arrData.length - 1 ].push( strMatchedValue );
    }
    return( arrData );
}

var ctx = document.getElementById("gamesPlayed").getContext("2d");

var games_per_day_data = CSVToArray(document.getElementById("games_per_day_chart_info").innerHTML, ",")[0]

var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [new Date(games_per_day_data[0]).toLocaleString(), new Date(games_per_day_data[1]).toLocaleString(), new Date(games_per_day_data[2]).toLocaleString(),new Date(games_per_day_data[3]).toLocaleString(),new Date(games_per_day_data[4]).toLocaleString(),new Date(games_per_day_data[5]).toLocaleString(),new Date(games_per_day_data[6]).toLocaleString(),new Date(games_per_day_data[7]).toLocaleString(),new Date(games_per_day_data[8]).toLocaleString(),new Date(games_per_day_data[9]).toLocaleString()],
        datasets: [{
            label: 'Games Played',
            data: [{
                t: new Date(games_per_day_data[0]),
                y: games_per_day_data[10]
            },
                {
                    t: new Date(games_per_day_data[1]),
                    y: games_per_day_data[11]
                },
                {
                    t: new Date(games_per_day_data[2]),
                    y: games_per_day_data[12]
                },
                {
                    t: new Date(games_per_day_data[3]),
                    y: games_per_day_data[13]
                },
                {
                    t: new Date(games_per_day_data[4]),
                    y: games_per_day_data[14]
                },
                {
                    t: new Date(games_per_day_data[5]),
                    y: games_per_day_data[15]
                },
                {
                    t: new Date(games_per_day_data[6]),
                    y: games_per_day_data[16]
                },
                {
                    t: new Date(games_per_day_data[7]),
                    y: games_per_day_data[17]
                },
                {
                    t: new Date(games_per_day_data[8]),
                    y: games_per_day_data[18]
                },
                {
                    t: new Date(games_per_day_data[9]),
                    y: games_per_day_data[19]
                },
            ],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255,99,132,1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    }
});

var top_5_player_data = CSVToArray(document.getElementById("top_5_winners_chart_info").innerHTML, ",")[0]

new Chart(document.getElementById("winsDonut"), {
    type: 'doughnut',
    data: {
        labels: [top_5_player_data[0], top_5_player_data[1], top_5_player_data[2], top_5_player_data[3], top_5_player_data[4]],
        datasets: [
            {
                label: "Wins",
                backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                data: [top_5_player_data[5],top_5_player_data[6],top_5_player_data[7],top_5_player_data[8],top_5_player_data[9]]
            }
        ]
    },
    options: {
        title: {
            display: true,
            text: 'Players With the Most Wins'
        }
    }
});

var top_5_game_data = CSVToArray(document.getElementById("top_5_games_chart_info").innerHTML, ",")[0]

new Chart(document.getElementById("popGame"), {
    type: 'radar',
    data: {
        labels: [top_5_game_data[0], top_5_game_data[1], top_5_game_data[2], top_5_game_data[3], top_5_game_data[4]],
        datasets: [
            {
                label: "Most Popular Game",
                fill: true,
                backgroundColor: "rgba(179,181,198,0.2)",
                borderColor: "rgba(179,181,198,1)",
                pointBorderColor: "#fff",
                pointBackgroundColor: "rgba(179,181,198,1)",
                data: [top_5_game_data[5], top_5_game_data[6],top_5_game_data[7],top_5_game_data[8],top_5_game_data[9]]
            },
        ]
    },
    options: {
        title: {
            display: true,
            text: 'Most Popular Games'
        }
    }
});