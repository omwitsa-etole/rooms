let constraints = {
  video: true,
  audio:true,
};

let video = document.getElementById("vid-stream");
const audio = document.querySelector("audio");

navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
  video.srcObject = stream;
  audio.srcObject = null;
});

function mute()
{
	var x = document.getElementById('mute');
	if(x.classList.contains('fa-microphone-slash'))
	{
		x.classList.remove('fa-microphone-slash');
		x.classList.add('fa-microphone');
		navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
		  audio.srcObject = stream;
		});
	}else{
		x.classList.remove('fa-microphone');
		x.classList.add('fa-microphone-slash');
		audio.srcObject = null;
	}
	
}
function closeShow()
{
	var x = document.getElementById('vid');
	//var y = document.getElementById('vidloader');
	if(x.classList.contains('fa-video'))
	{
		x.classList.remove('fa-video');
		x.classList.add('fa-video-slash');
		video.srcObject  = null;
		//y.style.display = 'block';
	}else{
		x.classList.remove('fa-video-slash');
		//y.style.display = 'none';
		
		navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
		  video.srcObject = stream;
		});
		x.classList.add('fa-video');
	}
}
function loadstation(){

	if(!window.navigator.onLine){
		document.getElementById('alert').style.display = 'block';
	}else{
		document.getElementById('alert').style.display = 'none';
	}
   setTimeout(loadstation, 5500); 	
}

function switchView(){
	var x= document.getElementById("view-1");
	var y = document.getElementById("view-2");
	var z = document.getElementById("vid");
	if(x.style.display == "none"){
		x.style.display = 'flex';
		y.style.display = 'none';
		video.srcObject = null;
		video = document.getElementById("vid-stream");
		if(z.classList.contains('fa-video-slash'))
		{
			video.srcObject = null;
		}else{
			navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
			  video.srcObject = stream;
			});
		}
	}else{
		x.style.display = 'none';
		y.style.display = 'flex';
		video.srcObject = null;
		video = document.getElementById("vid-stream-2");
		if(z.classList.contains('fa-video-slash'))
		{
			video.srcObject = null;
		}else{
			navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
			  video.srcObject = stream;
			});
		}
	}
	
}