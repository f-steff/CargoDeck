/*
Hide a DOM element with a given Id
*/
function hideElementId(hideId) {
    document.getElementById(hideID).style.display = 'none';
}

/*
Show a DOM element with a given Id
*/
function showElementId(showId) {
    document.getElementById(showId).style.display = 'block';
}

/*
Hide one, show another DOM element, both with given Ids.
*/
function HideId_ShowId(showId, hideId) {
	hideElementId(hideId);
	showElementId(showId);
}