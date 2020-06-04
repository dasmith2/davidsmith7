window.done_talking = false;
var utterance = new SpeechSynthesisUtterance('{{ say_this }}');
utterance.onend = function (event) {
  window.done_talking = true;
}
// The voice is a bit hard to understand. Slowing down from 1 to .9 helps a
// little.
utterance.rate = 0.9;
speechSynthesis.speak(utterance);
