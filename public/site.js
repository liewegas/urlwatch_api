function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

const app = document.getElementById('root');
const content = document.getElementById('content');

var site = getUrlVars()['site'];

document.getElementById('show_downtime').href = `?site=${site}&detail=downtime`;
document.getElementById('show_checks').href = `?site=${site}&detail=checks`;
document.getElementById('show_changes_filtered').href = `?site=${site}&detail=filtered`;
document.getElementById('show_changes_unfiltered').href = `?site=${site}&detail=unfiltered`;


function pc(f) {
    return (f * 100).toFixed(4)
}

function nice_time(t) {
    if (!t) {
	return '';
    }
    return new Date(t*1000).toISOString();
}

function nice_interval(t) {
    if (t < 120) {
	return `${t}s`;
    }
    t = Math.round(t / 60);
    if (t < 120) {
	return `${t}m`;
    }
    t = Math.round(t / 60);
    if (t < 48) {
	return `${t}h`;
    }
    t = Math.round(t / 24);
    return `${t}d`;
}

var request = new XMLHttpRequest();
request.open('GET', `http://${window.location.host}/api/sites/${site}/`);
request.onload = function() {
    var data = JSON.parse(this.response);

    document.getElementById('name').textContent = data['name'];
    document.getElementById('url').textContent = data['url'];    
    document.getElementById('url_link').href = data['url'];
    document.getElementById('hour').textContent = pc(data['uptime_hour']);
    document.getElementById('day').textContent = pc(data['uptime_day']);
    document.getElementById('week').textContent = pc(data['uptime_week']);
    document.getElementById('30_day').textContent = pc(data['uptime_30']);
    document.getElementById('90_day').textContent = pc(data['uptime_90']);
    document.getElementById('last_change').textContent = nice_time(data['last_change']);
    document.getElementById('last_up').textContent = nice_time(data['last_up']);
    document.getElementById('last_down').textContent = nice_time(data['last_down']);
    document.title = data['name']
}
request.send()



function show_downtime(guid) {
    var request = new XMLHttpRequest();
    var url = `http://${window.location.host}/api/sites/${site}/downtime/`;
    request.open('GET', url);
    request.onload = function() {
	var data = JSON.parse(this.response);
	var tabledata = [];
	console.log(data);
	for (var i = 0; i < data.length; i++) {
	    tabledata.push([nice_time(data[i]['start']),
			    nice_time(data[i]['end']),
			    nice_interval(data[i]['duration'])]);
	}
	$(document).ready(function() {
	    table = $('#table').DataTable( {
		data: tabledata,
		columns: [
		    { title: "start" },
		    { title: "end" },
		    { title: "duration" }
		],
		pageLength: 500,
		order: [[ 0, "desc" ]]
	    } );
	})
    }
    request.send();
}

function show_checks(guid, filtered) {
    var request = new XMLHttpRequest()
    url = 'http://' + window.location.host;
    if (filtered == 'filtered') {
	url += `/api/sites/${site}/get-changes-filtered`;
    } else if (filtered == 'unfiltered') {
	url += `/api/sites/${site}/get-changes-unfiltered`;
    } else if (filtered == 'downtime') {
	url += `/api/sites/${site}/get-downtime`;
    } else {
	url += `/api/sites/${site}/checks`;
    }
    console.log(url);
    request.open('GET', url);
    request.onload = function() {
	var data = JSON.parse(this.response);
	var tabledata = [];
	console.log(data);
	for (var i = 0; i < data.length; i++) {
	    var filtered_diff = '';
	    var unfiltered_diff = '';
	    if (i > 0) {
		var p = i - 1;
		if (data[i]['data'] &&
		    data[p]['data'] &&
		    data[i]['data'] != data[p]['data']) {
		    filtered_diff = ` (<a href="/api/blob-diff/${data[p]['data']}/${data[i]['data']}">diff</a>)`;
		}
		if (data[i]['data_unfiltered'] &&
		    data[p]['data_unfiltered'] &&
		    data[i]['data_unfiltered'] != data[p]['data_unfiltered']) {
		    unfiltered_diff = ` (<a href="/api/blob-diff/${data[p]['data_unfiltered']}/${data[i]['data_unfiltered']}">diff</a>)`;
		}
	    } else {
		filtered_diff = ' (initial)';
		unfiltered_diff = ' (initial)';
	    }
	    var filtered = '';
	    var unfiltered = '';
	    if (data[i]['tries'] == 0) {
		if (data[i]['data']) {
		    filtered = `<a href="/api/blob/${data[i]['data']}">${data[i]['data']}</a>${filtered_diff}`;
		}
		if (data[i]['data_unfiltered']) {
		    unfiltered = `<a href="/api/blob/${data[i]['data_unfiltered']}">${data[i]['data_unfiltered']}</a>${unfiltered_diff}`;
		}
	    }
	    tabledata.push([
		nice_time(data[i]['timestamp']),
		filtered, unfiltered])
	}
	console.log(tabledata);

	$(document).ready(function() {
	    table = $('#table').DataTable( {
		data: tabledata,
		columns: [
		    { title: "timestamp" },
		    { title: "data_filtered" },
		    { title: "data_unfiltered" }
		],
		pageLength: 500,
		order: [[ 0, "desc" ]]
	    } );
	})

    }
    request.send()
}

if (getUrlVars()['detail'] == 'checks') {
    show_checks(site, '');
}
if (getUrlVars()['detail'] == 'downtime') {
    show_checks(site, 'downtime');
}
if (getUrlVars()['detail'] == 'filtered') {
    show_checks(site, 'filtered');
}
if (getUrlVars()['detail'] == 'unfiltered') {
    show_checks(site, 'unfiltered');
}
if (getUrlVars()['detail'] == 'downtime') {
    show_downtime(site);
}

