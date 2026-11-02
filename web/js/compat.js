(function () {
  var button = document.getElementById('load');
  button.onclick = function () {
    var result = document.getElementById('result');
    result.innerHTML = 'Checking connection…';
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/library', true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) { return; }
      if (xhr.status !== 200) { result.innerHTML = 'Server connection failed: ' + xhr.status; return; }
      var list;
      try { list = JSON.parse(xhr.responseText); } catch (e) { result.innerHTML = 'Could not read library response.'; return; }
      if (!list.length) { result.innerHTML = 'Connected. Add an MP3 to the configured music directory, then tap again.'; return; }
      var track = list[0];
      var audio = document.getElementById('audio');
      audio.src = '/media/' + track.id;
      document.getElementById('download').href = '/download/' + track.id;
      document.getElementById('cover').src = track.art ? '/art/' + track.id : '';
      result.innerHTML = 'Connected. Probe track: ' + track.title + ' — ' + track.artist + '. Use the native controls to play and seek.';
      var lines = document.getElementById('lyrics');
      var lyricRequest = new XMLHttpRequest();
      lyricRequest.open('GET', '/api/lyrics/' + track.id, true);
      lyricRequest.onreadystatechange = function () {
        if (lyricRequest.readyState === 4 && lyricRequest.status === 200) {
          var parsed = JSON.parse(lyricRequest.responseText);
          lines.innerHTML = parsed.length ? parsed[0].text + (parsed[1] ? ' / ' + parsed[1].text : '') : 'LRC has no timed lines.';
        } else if (lyricRequest.readyState === 4) { lines.innerHTML = 'No associated LRC file found.'; }
      };
      lyricRequest.send(null);
    };
    xhr.send(null);
  };
}());
