const date = new Date();

function changeSel(day) {
	let val = day.innerText;
	let days = document.getElementsByTagName("li");
	for(let x = 0; x < days.length; x++) {
		let y = days[x];
		let span = document.querySelector('#sel');
		if (y.contains(span))
		{
			let val = y.innerText;
			y.innerHTML = `<li onclick = "changeSel(this)">${val}</li>`;
		}		
	}
	month_sel = document.querySelector(".month_name").innerT
	document.getElementById("dia").value = val.toString() + "/" + (date.getMonth() + 1).toString() + "/" + date.getFullYear().toString();
	day.innerHTML = `<li onclick = "changeSel(this)"><span id ="sel" class="selected">${val}</span></li>`;
}

const renderCalendar = () => {
	date.setDate(1);


const monthDays = document.querySelector(".days");

const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();

const prevLastDay = new Date(date.getFullYear(), date.getMonth(), 0).getDate();

const firstDayIndex = date.getDay();

const lastDayIndex = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDay();

const nextDays = 7 - lastDayIndex -1;

const months = [
"Enero",
"Febrero",
"Marzo",
"Abril",
"Mayo",
"Junio",
"Julio",
"Agosto",
"Septiembre",
"Octubre",
"Noviembre",
"Diciembre",
];

document.querySelector(".month_name").innerHTML = months[date.getMonth()];

let days = "";

for(let x = firstDayIndex; x > 0; x--) {
	days += `<li><span class="inactive">${prevLastDay - x +1}</span></li>`;
}

for (let i=1; i <= lastDay; i ++) {
	if(i === new Date().getDate() && date.getMonth() === new Date().getMonth())
	{
		days += `<li onclick = "changeSel(this)"><span class="active">${i}</span></li>`
	}
	else {
		days += `<li onclick = "changeSel(this)">${i}</li>`;
	}
}

for (let j=1; j <= nextDays; j ++) {
	days += `<li><span class="inactive">${j}</span></li>`;
	monthDays.innerHTML = days;
}

}



document.querySelector('.prev').
addEventListener('click', () => {
	date.setMonth(date.getMonth() -1);
	renderCalendar();
});

document.querySelector('.next').
addEventListener('click', () => {
	date.setMonth(date.getMonth() + 1);
	renderCalendar();
});

hoy = new Date()
document.getElementById("dia").value = hoy.getDate().toString() + "/" + (hoy.getMonth() + 1).toString() + "/" + hoy.getFullYear().toString();

renderCalendar();