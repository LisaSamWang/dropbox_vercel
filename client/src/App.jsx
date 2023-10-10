import HelloSign from 'hellosign-embedded';
import React, { useEffect, useState } from 'react';
import './MainPage.css';

function App() {
  const [transcript, setTranscript] = useState('');
  const [isSpeechDetected, setIsSpeechDetected] = useState(false);
  const [summary, setSummary] = useState('');
  const [speechTimestamps, setSpeechTimestamps] = useState([]);
  const [recognition, setRecognition] = useState(null);
  const [isStopButtonClicked, setIsStopButtonClicked] = useState(false);
  const [responses, setResponses] = useState([]);
  const [generatedResponses, setGeneratedResponses] = useState([]);
  const [isGeneratingResponses, setIsGeneratingResponses] = useState(false);

  const appendTranscriptWithTimestamp = (newTranscript) => {
    const currentTime = new Date().toLocaleTimeString();
    const newSpeech = `${currentTime}: ${newTranscript}`;
    setTranscript((prevTranscript) => prevTranscript + '\n' + newSpeech);
    setSpeechTimestamps((prevTimestamps) => [...prevTimestamps, newSpeech]);
    setIsSpeechDetected(true);
  };

  const startSpeechRecognition = () => {
    const recognitionInstance = new window.webkitSpeechRecognition();
    recognitionInstance.continuous = true;

    recognitionInstance.onresult = function (event) {
      const newTranscript = event.results[event.results.length - 1][0].transcript;
      appendTranscriptWithTimestamp(newTranscript);
    };

    recognitionInstance.onstart = function () {
      setIsSpeechDetected(true);
      setIsStopButtonClicked(false);
      console.log('start');
    };

    recognitionInstance.onend = function () {
      setIsSpeechDetected(false);
      console.log('end');
      if (isStopButtonClicked) {
        startSummarization();
      }
    };

    recognitionInstance.start();
    setRecognition(recognitionInstance);
  };

  const stopSpeechRecognition = () => {
    if (recognition) {
      recognition.stop();
      setIsStopButtonClicked(true);
      startSummarization();
    }
  };

  const eraseTranscription = () => {
    setTranscript('');
    setSummary('');
    setIsSpeechDetected(false);
    setSpeechTimestamps([]);
  };

  const startSummarization = () => {
    if (!isSpeechDetected) {
      const transcriptData = transcript;

      if (transcriptData) {
        console.log('Starting summarization...');
        // fetch('http://localhost:8080/summarize', {
        fetch('"https://dropbox-backend.onrender.com/api/summarize"', {
          method: 'POST',
          body: JSON.stringify({ transcript: transcriptData }),
          headers: {
            'Content-Type': 'application/json',
          },
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error('Network response error');
            }
            return response.json();
          })
          .then((data) => {
            console.log('Res from backend:', data);
            const newSummary = data.summary;
            console.log('Summary from response:', newSummary);

            if (newSummary !== undefined) {
              setSummary(newSummary);
            } else {
              console.error('Summary is undefined.');
            }

            setResponses(data.responses);
            setGeneratedResponses(data.responses);
            console.log('Summary generated successfully:', newSummary);
          })
          .catch((error) => {
            console.error('Error:', error);
          });
      } else {
        console.log('Transcript data is empty.');
      }
    } else {
      console.log('Speech is still detected.');
    }
    setIsSpeechDetected(false);
  };


  useEffect(() => {
    if (transcript !== '' && !isSpeechDetected) {
      startSummarization();
    }
  }, [transcript, isSpeechDetected]);

  useEffect(() => {
    if (isGeneratingResponses) {
      // fetch("http://localhost:8080/summarize", {
      fetch('"https://dropbox-backend.onrender.com/api/summarize"', {
        method: 'POST',
        body: JSON.stringify({ transcript: transcript }),
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Network response error');
          }
          return response.json();
        })
        .then((data) => {
          const generatedSummary = data.summary;
          const generatedResponses = data.responses;
          setSummary(generatedSummary);
          setGeneratedResponses(generatedResponses);
          setIsGeneratingResponses(false);
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }
  }, [transcript, isGeneratingResponses]);



  // const fetchResponses = () => {
  //   setIsGeneratingResponses(true);
  // };

  const renderGeneratedResponses = () => {
    if (generatedResponses.length === 0) {
      return <p class="generatetext">No generated responses available.</p>;
    }

    return (
      <div id="generatedResponses">
        {generatedResponses.map((response, index) => (
          <p class="generatetext" key={index}>{response}</p>
        ))}
      </div>
    );
  };

  const client = new HelloSign();

  const openSign = () => {
    fetch("http://localhost:8080/api/dropbox", {
      method: 'GET',
      mode: 'no-cors', // Set the mode option to 'no-cors'
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.text())
      .then(result => console.log(result))
      .catch(error => console.log('error', error));
  }

  return (
    <div className="App">
    <div class="one">
      <h1 >
        Audio-to-Agreemen
        <span>by LegalEase</span>
      </h1>
    </div>
      

      {/* Step 1: user uploads an audio file */}
      <form method="post" encType="multipart/form-data">
        <input type="file" name="file" accept=".mp3, .wav, .ogg" hidden />
        <input type="submit" value="Transcribe" hidden />
      </form>

      {/* Step 2: display transcribed text */}
      <div class= 'section-header'>Audio Record Agreement Details</div>
      <div class= 'instructions'>real time audio input for agreement details</div>
 
      <div class='button-container'>
        <button class='button -green center' onClick={startSpeechRecognition}>Start Speech</button>
        <button class='button -salmon center' onClick={stopSpeechRecognition}>Stop Speech</button>
        <button class='button -dark center' onClick={eraseTranscription}>Erase</button>
      </div>

      <div id='trascript-container'>
      {transcript === '' ? (
        <div id="transcription"><div>Say Something</div></div>
      ) : (
        <div id="speechTranscriptContainer">
          <div id="transcription">
            <div>Transcribed Text</div>
            {/* <p>{transcript}</p> */}
          </div>
        </div>
      )}

      {/* Display speech timestamps */}
      <div id="speechTimestamps">
        {speechTimestamps.map((timestamp, index) => (
          <p key={index}>{timestamp}</p>
        ))}
      </div>
      </div>

      {/* Step 3: display the summary */}
      <div id="summaryContainer">
        <div class='summary-title'>Summary</div>
        {summary !== "" ? (
          <div id="summary">{summary}</div>
        ) : (
          <div id="nosummary">No summary available.</div>
        )}
      </div>

      {/* Step 4: generate agreements */}
      <div id="generatedResponses">
        <div class='generate-title'>Generated Responses</div>
        {renderGeneratedResponses()}
      </div>

      {/* Step 5: user feedback and modification using audio file upload */}
      <div className='review-container'>
      <div class='section-header'>Review and Modify Agreements</div>
      <div class= 'instructions'></div>

      <form class= "upload" action="/modify" method="POST" encType="multipart/form-data">
        <input type="file" name="audio_feedback" accept=".mp3, .wav, .ogg" />
        <input type="submit" value="Upload Audio Feedback" />
      </form>
      </div>
      {/* Step 6: ai suggestions */}
      <div class="review-container">
      <div class='section-header'>AI Suggestion</div>
      <div class= 'instructions'>AI-generated suggestions based on user feedback will display here</div>
      </div>


      {/* Step 7: finalise & download agreements */}
      <div class="review-container">
        <div class="section-header">Download</div>
        <div class="upload"> 
        <a class="downloadlink" href="/download">Download Customized Agreements</a> 
        <button class='button -salmon center' onClick={openSign}>Click Here To Sign</button>
        </div>
       
      </div>

      {/* Future features - will leave it here for now and check off later */}
      <div class='section-header'>Future Features</div>
      <ul className="future-features">
        <li>Live translation</li>
        <li>Read agreements aloud</li>
        <li>Auto-sign certain documents</li>
        <li>Remove signatures</li>
        <li>Manage document collections</li>
      </ul>
    </div>
  );
}

export default App;
