var dataCsv = d3.csv("../../data/annual_repurchase_curves.csv?t=${Date.now()}");

dataCsv.then(function (data) {
    var elem = document.getElementById('chart-select');
    makeChart(filteredData(elem.value))
    elem.addEventListener("change", onSelectChange);

    var count_or_upb = document.querySelector('input[name="flexRadioDefault"]');
    makeLineChart(data, count_or_upb.value)

    if (document.querySelector('input[name="flexRadioDefault"]')) {
        document.querySelectorAll('input[name="flexRadioDefault"]').forEach((elem) => {
            elem.addEventListener("change", function (event) {
                var item = event.target.value;
                makeLineChart(data, item)
            });
        });
    }


    function filteredData(value) {
        var filterdata = data.filter(function (d, i) {
            if (d['LOAN_AGE'] == value) {
                return d;
            }
        })
        return filterdata
    }

    function onSelectChange() {
        var value = this.value;
        var fdata = filteredData(value);
        makeChart(fdata)
    }

    function onSelectRadio() {
        var value = this.value;
    }

});


function makeLineChart(data, count_or_upb) {

    const unique = [...new Set(data.map(item => item.ORIG_YEAR))];

    function filteredData2(value) {
        var filterdata = data.filter(function (d, i) {
            if (d['ORIG_YEAR'] == value) {
                return d;
            }
        })
        return filterdata
    }



    var currentMode;
    if (count_or_upb == "age_repurch_rate") {
        currentMode = 'age_repurch_rate'
    } else if (count_or_upb == 'age_repurch_orig_upb_at_terminal_rate') {
        currentMode = 'age_repurch_orig_upb_at_terminal_rate'
    } else {
        currentMode = 'age_repurch_upb_rate'
    }

    chart_data = []

    for (var i = 0; i < unique.length; i++) {
        vintage_data = filteredData2(unique[i])
        var LOAN_AGE = [],
            age_repurch_rate = [];
        vintage_data.map(function (d) {
            LOAN_AGE.push(d.LOAN_AGE);
            age_repurch_rate.push(d[currentMode]);
        })
        var result = {
            x: LOAN_AGE,
            y: age_repurch_rate,
            type: 'scatter',
            mode: 'lines',
            name: unique[i]
        };
        chart_data.push(result);

    }

    var layout = {
        title: {
            text: 'Cumulative repurchase rates by cohort'
        }
    };


    Plotly.newPlot('myDiv', chart_data, layout);
}

function makeChart(data) {
    var ORIG_YEAR = [],
        age_ult_diff = [],
        age_repurch_rate = [];
    data.map(function (d) {
        ORIG_YEAR.push(d.ORIG_YEAR);
        age_ult_diff.push(d.age_ult_diff);
        age_repurch_rate.push(d.age_repurch_rate);
    })

    var config = { responsive: true };

    var trace1 = {
        x: ORIG_YEAR,
        y: age_repurch_rate,
        type: 'bar',
        name: 'Repurchase rate through months selected'
    }

    var trace2 = {
        x: ORIG_YEAR,
        y: age_ult_diff,
        type: 'bar',
        name: 'Total cumulative repurchase rate'
    }

    var data = [trace1, trace2];

    var layout = {
        barmode: 'stack',
        title: {
            text: 'Repurchase rates by cohort'
        },
        legend: { "orientation": "h" }
    };

    TESTER = document.getElementById('test');
    Plotly.newPlot(TESTER, data, layout, config);

    TESTER.on('plotly_click', function (data) {
        console.log(data.points[1].x)
        var pts = '';
        for (var i = 0; i < data.points.length; i++) {
            pts = 'x = ' + data.points[i].x + '\ny = ' +
                data.points[i].y.toPrecision(4) + '\n\n';
        }
    });

}