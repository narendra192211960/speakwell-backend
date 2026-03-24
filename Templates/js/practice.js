(function() {
    // Pre-initialize voices for better performance on first click
    window.speechSynthesis.getVoices();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }

    // Local Session State
    let session = {
        title: "Practice Session",
        items: [],
        currentIndex: 0,
        scores: [],
        sessionResults: [], // Track individual item results
        sessionId: "",      // Unique ID for the session
        isRecording: false,
        isPaused: false,
        recognition: null,
        startTime: null,
        totalDuration: 0,
        currentTranscript: "",
        category: "",
        visualizer: null,
        audioCtx: null,
        analyser: null
    };

    const VOWEL_ITEMS = [
        "eat eat eat", "it it it", "ice ice ice", "at at at", 
        "hot hot hot", "out out out", "boot boot boot", "but but but"
    ];

    const WORD_ITEMS = [
        "hello hello hello", "thank you thank you thank you", "water water water",
        "food food food", "help help help", "yes yes yes",
        "no no no", "please please please", "home home home",
        "sorry sorry sorry", "doctor doctor doctor", "phone phone phone",
        "money money money", "friend friend friend", "family family family"
    ];

    const NUMBER_ITEMS = [
        "One One One", "Two Two Two", "Three Three Three",
        "Four Four Four", "Five Five Five", "Six Six Six",
        "Seven Seven Seven", "Eight Eight Eight", "Nine Nine Nine", "Ten Ten Ten"
    ];

    const CONSONANT_ITEMS = [
        "Red Red Red", "Led Led Led", "Right Right Right",
        "Light Light Light", "Road Road Road", "Load Load Load",
        "Pray Pray Pray", "Play Play Play", "Rice Rice Rice",
        "Lice Lice Lice", "Read Read Read", "Lead Lead Lead"
    ];

    const PARAGRAPH_ITEMS = [
        "I wake up early. I drink water and eat breakfast. I start my day with a smile.",
        "I went to the market with my friend. We bought milk and fruits. It was a good day.",
        "I practice my speech every day. I speak clearly and slowly. This helps me improve.",
        "We planned a short trip. The weather was cool and pleasant. We enjoyed a lot.",
        "Helping others is a good habit. I speak kindly. Good words make people happy."
    ];

    const SENTENCE_ITEMS = [
        "How are you today?",
        "I am feeling well.",
        "The weather is nice.",
        "Thank you very much.",
        "Please open the door.",
        "I will try again.",
        "This is very good.",
        "Can you help me?"
    ];

    const TH_SOUND_ITEMS = [
        "the the the", "this this this", "that that that", "three three three", 
        "think think think", "thank thank thank", "mother mother mother", "father father father"
    ];

    const COMPLEX_SENTENCE_ITEMS = [
        "I would like to schedule an appointment.", "Could you please help me with this?", 
        "The rehabilitation program is very helpful.", "I have been practicing every single day.", 
        "I am trying to improve my speech step by step.", "The doctor advised me to practice slowly and clearly.", 
        "Recording my voice helps me understand my mistakes.", "Consistent practice will improve my communication skills."
    ];

    const TONGUE_TWISTER_ITEMS = [
        "She sells seashells by the seashore.", "Peter Piper picked a peck of pickled peppers.", 
        "Red lorry, yellow lorry.", "Betty bought butter but the butter was bitter.", 
        "Fresh fried fish, fresh fried fish."
    ];

    const MEDICAL_ITEMS = [
        "rehabilitation", "therapy", "medication", "appointment", 
        "diagnosis", "treatment", "recovery", "exercise"
    ];

    function init() {
        const exercise = JSON.parse(localStorage.getItem('selected_exercise'));
        const category = localStorage.getItem('selected_category');
        
        session.sessionId = "sess_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
        session.category = category || "vowels";
        const storedTitle = localStorage.getItem('selected_title');
        session.title = exercise ? exercise.title : (storedTitle || session.category.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));

        // Category-based item loading - aligned with app fallback lists
        if (session.title === "TH Sound Practice") {
            session.items = TH_SOUND_ITEMS;
        } else if (session.title === "Complex Sentences") {
            session.items = COMPLEX_SENTENCE_ITEMS;
        } else if (session.title === "Medical Terminology") {
            session.items = MEDICAL_ITEMS;
        } else if (session.title === "Tongue Twisters") {
            session.items = TONGUE_TWISTER_ITEMS;
        } else {
            // General category fallback
            switch(session.category) {
                case "vowels":
                    session.items = VOWEL_ITEMS;
                    break;
                case "words":
                    session.items = WORD_ITEMS;
                    break;
                case "numbers":
                    session.items = NUMBER_ITEMS;
                    break;
                case "consonants":
                    session.items = CONSONANT_ITEMS;
                    break;
                case "paragraphs":
                    session.items = PARAGRAPH_ITEMS;
                    break;
                case "sentences":
                    session.items = SENTENCE_ITEMS;
                    break;
                case "fluency":
                    session.items = TONGUE_TWISTER_ITEMS;
                    break;
                case "self_exercise":
                    session.items = ["Choose your own topic and then speak at least 3 minutes"];
                    break;
                default:
                    session.items = exercise ? [exercise.text] : ["Hello World"];
            }
        }

        updateHeader();
        showPhase('instruction');
        bindEvents();
    }

    function updateHeader() {
        document.getElementById('practiceTitle').textContent = session.title;
        const current = session.currentIndex + 1; // Start from 1
        const total = session.items.length;
        document.getElementById('progressCount').textContent = `${current} / ${total}`;
        const percent = total > 0 ? Math.round((current / total) * 100) : 0;
        document.getElementById('progressBar').style.width = `${percent}%`;
        document.getElementById('progressPercent').textContent = `${percent}%`;
    }

    function showPhase(phase) {
        // Phases: instruction, practice, analyzing, result, complete
        const phases = ['instructionPhase', 'practicePhase', 'analyzingPhase', 'resultSection', 'completePhase'];
        phases.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });

        const targetId = phase === 'result' ? 'resultSection' : phase + 'Phase';
        const target = document.getElementById(targetId);
        if (target) target.style.display = 'flex'; // Use flex for centering if CSS allows
        
        // Hide/Show header based on phase
        const header = document.querySelector('.exercise-header');
        if (header) {
            header.style.display = (phase === 'complete' ? 'none' : 'flex');
        }

        if (phase === 'practice' || phase === 'instruction') {
            if (header) header.style.display = 'flex';
        }

        if (phase === 'practice') {
            loadCurrentItem();
        }
    }

    function loadCurrentItem() {
        const word = session.items[session.currentIndex];
        document.getElementById('wordDisplay').textContent = word;
        
        // Reset UI for item
        session.currentTranscript = ""; // Reset transcript on load/retry
        document.getElementById('initialPracticeUI').style.display = 'block';
        document.getElementById('recordingUI').style.display = 'none';
        
        updateHeader();
    }

    function playExample() {
        const word = session.items[session.currentIndex];
        if (!word) return;
        
        // Cancel any pending speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(word);
        
        // Advanced high-quality voice selection
        const voices = window.speechSynthesis.getVoices();
        
        // Priority list for premium voice keywords
        const priorityKeywords = ["Google", "Natural", "Neural", "HD", "Premium", "Pro"];
        
        let bestVoice = null;
        
        // 1. Try to find a US English voice with premium keywords
        for (const kw of priorityKeywords) {
            bestVoice = voices.find(v => v.lang.startsWith('en-US') && v.name.includes(kw));
            if (bestVoice) break;
        }
        
        // 2. Fallback to any US English voice
        if (!bestVoice) {
            bestVoice = voices.find(v => v.lang.startsWith('en-US'));
        }
        
        // 3. Fallback to any English voice (GB/AU etc) with premium keywords
        if (!bestVoice) {
            for (const kw of priorityKeywords) {
                bestVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes(kw));
                if (bestVoice) break;
            }
        }

        if (bestVoice) {
            utterance.voice = bestVoice;
            console.log("Selected voice for clarity:", bestVoice.name);
        }
        
        utterance.lang = 'en-US';
        utterance.rate = 0.9;  // Slightly faster than 0.8 for better clarity/less slurring
        utterance.pitch = 1.0; // Keep pitch natural
        utterance.volume = 1.0; 
        
        window.speechSynthesis.speak(utterance);
    }

    function bindEvents() {
        // Let's Begin
        document.getElementById('btnLetsBegin').onclick = () => {
            showPhase('practice');
        };

        // Exit
        document.getElementById('exitSessionBtn').onclick = () => {
            stopAllMedia();
            window.history.back();
        };
        document.getElementById('btnBackToTraining').onclick = () => {
            stopAllMedia();
            window.history.back();
        };

        // Play Example
        document.getElementById('btnPlayExample').onclick = playExample;

        // Recording
        document.getElementById('btnTapToRecord').onclick = startRecording;
        document.getElementById('btnStopRecord').onclick = stopRecording;
        
        const btnPauseResume = document.getElementById('btnPauseResume');
        const pauseBtnText = document.getElementById('pauseBtnText');

        if (btnPauseResume) {
            btnPauseResume.onclick = () => {
                if (!session.isRecording) return;
                
                if (session.isPaused) {
                    // Resume
                    session.isPaused = false;
                    if(pauseBtnText) pauseBtnText.textContent = "Pause";
                    document.getElementById('recordingStatus').textContent = "Listening...";
                    try { session.recognition.start(); } catch(e) {}
                    // Resume visualization
                    if (session.audioCtx && session.audioCtx.state === 'suspended') {
                        session.audioCtx.resume();
                    }
                } else {
                    // Pause
                    session.isPaused = true;
                    if(pauseBtnText) pauseBtnText.textContent = "Resume";
                    document.getElementById('recordingStatus').textContent = "Paused";
                    try { session.recognition.stop(); } catch(e) {}
                    // Pause visualization
                    if (session.audioCtx && session.audioCtx.state === 'running') {
                        session.audioCtx.suspend();
                    }
                }
            };
        }

        // Results
        document.getElementById('btnNextWord').onclick = nextItem;
        document.getElementById('btnTryAgain').onclick = () => showPhase('practice');
        document.getElementById('btnFinishExercise').onclick = finishSession;

        // Completion
        const btnPracticeAgain = document.getElementById('btnPracticeAgain');
        if (btnPracticeAgain) {
            btnPracticeAgain.onclick = () => {
                session.currentIndex = 0;
                session.scores = [];
                session.sessionResults = [];
                showPhase('instruction');
            };
        }
    }

    async function startRecording() {
        // Re-bind to ensure elements are current
        bindEvents();

        // Request mic permission ONLY when "Tap to Record" is clicked
        if (!session.micStream) {
            try {
                session.micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            } catch (err) {
                console.warn("[Practice] Mic permission denied:", err);
                alert("Microphone permission is required to record your voice.");
                return;
            }
        }

        // Immediate UI feedback
        document.getElementById('initialPracticeUI').style.display = 'none';
        document.getElementById('recordingUI').style.display = 'flex';
        document.getElementById('recordingStatus').textContent = "Listening...";
        
        const pauseBtnText = document.getElementById('pauseBtnText');
        if (pauseBtnText) pauseBtnText.textContent = "Pause";


        // Always recreate recognition for reliability
        if (session.recognition) {
            try { session.recognition.stop(); } catch(e) {}
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Speech recognition not supported in this browser.");
            return;
        }
        session.recognition = new SpeechRecognition();
        session.recognition.continuous = true;
        session.recognition.interimResults = true;
        session.recognition.lang = 'en-US';
        session.currentTranscript = "";

        session.recognition.onstart = () => {
            session.isRecording = true;
            session.isPaused = false;
            session.startTime = Date.now();
            console.log("[Practice] Recording started.");
            
            // Start visualizer
            if (session.micStream) initVisualizer(session.micStream);
        };

        session.recognition.onresult = (event) => {
            let finalTranscript = "";
            let interimTranscript = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
                else interimTranscript += event.results[i][0].transcript;
            }
            const current = finalTranscript || interimTranscript;
            if (current) {
                session.currentTranscript = current;
                document.getElementById('recordingStatus').textContent = `"${current}..."`;
            }
        };

        session.recognition.onerror = (event) => {
            console.error("[Practice] Recognition Error:", event.error);
            if (event.error === 'not-allowed') alert("Please allow microphone access.");
        };

        session.recognition.onend = () => {
            if (session.isRecording && !session.isPaused) {
                try { session.recognition.start(); } catch(e) {}
            }
        };

        try {
            session.recognition.start();
            if (session.micStream) initVisualizer(session.micStream);
        } catch (err) {
            console.warn("[Practice] Start error:", err.message);
        }
    }

    function initVisualizer(stream) {
        if (!window.AudioContext && !window.webkitAudioContext) return;
        
        try {
            if (!session.audioCtx) {
                session.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (session.audioCtx.state === 'suspended') {
                session.audioCtx.resume();
            }
            
            session.analyser = session.audioCtx.createAnalyser();
            const source = session.audioCtx.createMediaStreamSource(stream);
            source.connect(session.analyser);
            session.analyser.fftSize = 512;


            const bufferLength = session.analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            const bars = document.querySelectorAll('#waveformContainer .wave-bar');

            function draw() {
                if (!session.isRecording || !session.analyser) return;
                
                requestAnimationFrame(draw);
                
                if (session.isPaused) {
                    // Visually stop bars by setting them to minimum height
                    for (let i = 0; i < bars.length; i++) {
                        bars[i].style.height = '12px';
                    }
                    return;
                }

                session.analyser.getByteFrequencyData(dataArray);
                
                // Map frequencies to the bars with higher sensitivity
                for (let i = 0; i < bars.length; i++) {
                    const index = Math.floor(i * (bufferLength / bars.length) * 0.5) + 2; 
                    const val = dataArray[index] || 0; 
                    // Higher sensitivity and floor
                    const height = Math.max(12, (val / 255) * 120);
                    bars[i].style.height = height + 'px';
                }
            }
            
            draw();
        } catch (e) {
            console.error("[Practice] Visualizer error:", e);
        }
    }

    function stopRecording() {
        if (!session.isRecording) return;
        session.isRecording = false;
        session.isPaused = false;
        
        // Final attempt to get transcript from recognition if it's still running
        if (session.recognition) {
            try { session.recognition.stop(); } catch(e) {}
        }
        
        showPhase('analyzing');
        
        const duration = Math.round((Date.now() - session.startTime) / 1000);
        session.totalDuration += duration;

        // Simulate analysis delay
        setTimeout(() => {
            try {
                finalizeResults();
            } catch (err) {
                console.error("[Practice] Error in finalizeResults:", err);
                showPhase('practice'); // Fallback to practice if it crashes
            }
        }, 2000);
    }

    function processResults() {
        showPhase('analyzing');
        
        // Short delay to simulate AI processing as in the app
        setTimeout(() => {
            finalizeResults();
        }, 2000);
    }

    function finalizeResults() {
        let item = session.items[session.currentIndex];
        let target = typeof item === 'object' ? (item.title || item.text || "") : item;
        const actual = session.currentTranscript || "";
        
        if (!actual) {
            session.scores.push(0); 
            showItemResult(0, "No speech detected", target);
            return;
        }

        const accuracy = calculateAccuracy(target, actual);
        session.scores.push(accuracy);
        
        showItemResult(accuracy, actual, target);
    }

    function showItemResult(accuracy, actual, target) {
        showPhase('result');
        const scoreEl = document.getElementById('itemScore');
        const transEl = document.getElementById('itemTranscript');
        const feedbackEl = document.getElementById('itemFeedback');

        scoreEl.textContent = `Accuracy: ${accuracy}%`;
        transEl.textContent = `You Said: "${actual || "No speech detected"}"`;
        
        let feedback = "";
        let feedbackColor = "";

        if (!actual || actual === "No speech detected") {
            feedback = "No speech detected. Please try again.";
            feedbackColor = "#64748b"; // Gray
        } else if (accuracy >= 90) {
            feedback = "Excellent! Your pronunciation is clear.";
            feedbackColor = "#22c55e"; // Green
        } else if (accuracy >= 70) {
            feedback = "Good job! Keep practicing.";
            feedbackColor = "#f59e0b"; // Orange
        } else if (accuracy >= 40) {
            feedback = "Not bad, but try to focus on the sounds.";
            feedbackColor = "#ef4444"; // Red
        } else {
            feedback = "Let's try that again. Focus on each word.";
            feedbackColor = "#ef4444"; // Red
        }
        
        feedbackEl.textContent = feedback;
        feedbackEl.style.color = feedbackColor;

        // Show appropriate buttons based on whether it's the last word
        const isLast = session.currentIndex === session.items.length - 1;
        
        if (isLast) {
            document.getElementById('btnNextWord').style.display = 'none';
            document.getElementById('btnFinishExercise').style.display = 'block';
        } else {
            document.getElementById('btnNextWord').style.display = 'block';
            document.getElementById('btnFinishExercise').style.display = 'none';
        }
        document.getElementById('btnTryAgain').style.display = 'block';

        // Add to session results for final saving
        session.sessionResults.push({
            expected: target,
            actual: actual,
            accuracy: accuracy,
            feedback: feedback
        });
    }

    function calculateAccuracy(target, actual) {
        if (!actual) return 0;
        const targetWords = target.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).filter(w => w.length > 0);
        const actualWordsList = actual.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).filter(w => w.length > 0);
        
        // Use frequency mapping to handle repeated words accurately
        const actualFreq = {};
        actualWordsList.forEach(w => {
            actualFreq[w] = (actualFreq[w] || 0) + 1;
        });

        let matches = 0;
        targetWords.forEach(word => {
            if (actualFreq[word] && actualFreq[word] > 0) {
                matches++;
                actualFreq[word]--;
            }
        });

        return Math.round((matches / targetWords.length) * 100);
    }

    function nextItem() {
        session.currentIndex++;
        session.currentTranscript = "";
        
        if (session.currentIndex >= session.items.length) {
            finishSession();
        } else {
            showPhase('practice');
        }
    }

    async function finishSession() {
        const avgScore = session.scores.length > 0 ? Math.round(session.scores.reduce((a, b) => a + b, 0) / session.scores.length) : 0;
        
        document.getElementById('finalAvgAccuracy').textContent = `${avgScore}%`;
        document.getElementById('finalWordsPracticed').textContent = session.sessionResults.length;
        
        // Show complete phase immediately so user sees trophy
        showPhase('complete');

        // Save to backend dynamically
        const userId = Auth.getUserId();
        if (userId && session.sessionResults.length > 0) {
            console.log(`[Practice] Saving ${session.sessionResults.length} attempts...`);
            try {
                // Save each attempt in the session
                const savePromises = session.sessionResults.map(res => {
                    return API.saveAttempt(
                        userId, 
                        session.sessionId, // session_id
                        session.title,     // exercise_name
                        res.expected,      // expected_sentence
                        res.actual,        // recognized_text
                        res.accuracy,      // accuracy
                        res.feedback       // feedback
                    );
                });
                
                await Promise.all(savePromises);
                console.log("[Practice] All attempts saved successfully.");
                
                // Trigger a global refresh so that when they navigate back, data is hot
                if (window.refreshAllStats) {
                    await window.refreshAllStats();
                }
            } catch (err) {
                console.error("[Practice] Failed to save some attempts:", err);
            }
        }
    }

    function stopAllMedia() {
        if (session.micStream) {
            session.micStream.getTracks().forEach(track => track.stop());
            session.micStream = null;
        }
        if (session.recognition) {
            try { session.recognition.stop(); } catch(e) {}
            session.recognition = null;
        }
    }

    // Start initialization
    init();

})();
