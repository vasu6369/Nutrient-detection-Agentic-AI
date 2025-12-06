import React, { useEffect, useRef, useState } from "react";
import "./App.css";

const TTS_API_URL = "http://127.0.0.1:8000/tts";

async function playTts(text) {
    if (!text || !text.trim()) return;

    const formData = new FormData();
    formData.append("text", text);

    try {
        const res = await fetch(TTS_API_URL, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            console.error("TTS error:", await res.text());
            return;
        }

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
    } catch (err) {
        console.error("TTS fetch failed:", err);
    }
}


// --- Simple SVG Icons Components ---
const IconPlant = () => (
    <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M7 17v-6a3 3 0 0 1 3-3h0a4 4 0 0 1 4 4v5" />
        <path d="M12 17v-6.5a3.5 3.5 0 0 0-3.5-3.5h0a3.5 3.5 0 0 0-3.5 3.5v3" />
        <path d="M12 17v4" />
        <path d="M9 21h6" />
    </svg>
);

const IconMic = ({ active }) => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill={active ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
        <line x1="12" y1="19" x2="12" y2="23" />
        <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
);

const IconSend = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <line x1="22" y1="2" x2="11" y2="13" />
        <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
);

const IconPlus = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
);

const IconImage = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
    </svg>
);

const IconRefresh = () => (
    <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <polyline points="23 4 23 10 17 10" />
        <polyline points="1 20 1 14 7 14" />
        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
);

const IconBot = () => (
    <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="var(--accent)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" />
        <path d="M4 10a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8z" />
        <line x1="12" y1="8" x2="12" y2="10" />
        <line x1="8" y1="14" x2="8" y2="14" />
        <line x1="16" y1="14" x2="16" y2="14" />
        <path d="M9 18h6" />
    </svg>
);

export default function App() {
    // ---- State ----
    const [messages, setMessages] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [userInput, setUserInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [conversationStarted, setConversationStarted] = useState(false);
    const [lastServerResponse, setLastServerResponse] = useState(null);

    // voice
    const [recording, setRecording] = useState(false);
    const [voiceMode, setVoiceMode] = useState(false);

    // 🔊 text-to-speech state
    const [ttsState, setTtsState] = useState({
        status: "idle",       // "idle" | "speaking" | "paused"
        messageId: null,      // which message is being read
    });
    const [isDragOver, setIsDragOver] = useState(false);


    // 🔊 audio refs for Edge TTS
    const audioRef = useRef(null);        // current Audio object
    const audioUrlRef = useRef(null);

    // refs
    const inputRef = useRef(null);
    const fileRef = useRef(null);
    const chatHistoryRef = useRef(null);

    // recognition-related refs
    const recognitionRef = useRef(null);
    const keepListeningRef = useRef(false);
    const isRestartingRef = useRef(false);
    const errorBackoffRef = useRef({ count: 0, lastError: null });
    const confirmedTranscriptRef = useRef("");
    const isSendingRef = useRef(false);
    const fetchControllerRef = useRef(null);

    const SpeechRecognition =
        typeof window !== "undefined" &&
        (window.SpeechRecognition || window.webkitSpeechRecognition);

    // ---- effects ----

    // Auto-scroll to latest message whenever messages change
    useEffect(() => {
        const el = chatHistoryRef.current;
        if (!el) return;

        el.scrollTo({
            top: el.scrollHeight,
            behavior: "smooth",
        });

        setTimeout(() => {
            el.scrollTop = el.scrollHeight;
        }, 150);
    }, [messages]);

    useEffect(() => {
        if (!voiceMode && !loading) inputRef.current?.focus();
    }, [voiceMode, loading]);

    useEffect(() => {
        return () => {
            stopVoiceInput(true);
            try {
                window.speechSynthesis?.cancel();
            } catch (e) {}

            // 🔊 stop any playing audio & free URL
            if (audioRef.current) {
                try {
                    audioRef.current.pause();
                } catch (e) {}
            }
            if (audioUrlRef.current) {
                try {
                    URL.revokeObjectURL(audioUrlRef.current);
                } catch (e) {}
            }

            if (previewUrl)
                try {
                    URL.revokeObjectURL(previewUrl);
                } catch (e) {}
            try {
                fetchControllerRef.current?.abort();
            } catch (e) {}
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);


    // ---- helpers ----
    const pushMessage = (role, text) => {
        const id =
            typeof crypto !== "undefined" && crypto.randomUUID
                ? crypto.randomUUID()
                : Date.now() + Math.random();
        setMessages((p) => [...p, { id, role, text }]);
    };

    const cleanText = (text) => {
        return text
            .replace(/\*\*/g, "")   // remove bold markdown
            .replace(/\*/g, "")     // remove leftover asterisk
            .replace(/_/g, "")      // remove italics
            .replace(/:\s*/g, " ")  // remove colon sounds
            .replace(/[{}\[\]"]/g, "") // remove JSON symbols
            .replace(/[-•]/g, " ")  // replace bullets with space
            .replace(/\n{2,}/g, ". ") // paragraph breaks
            .replace(/\n/g, ", ")   // line breaks
            .replace(/\s{2,}/g, " ") // collapse spaces
            .trim();
    };


    const speak = (text, messageId) => {
        if (!("speechSynthesis" in window)) return;

        const synth = window.speechSynthesis;
        try {
            synth.cancel();
        } catch (e) {}

        const cleaned = cleanText(text);
        if (!cleaned) return;

        // Split into sentences so TTS adds natural pauses
        const sentences = cleaned.match(/[^.!?]+[.!?]?/g) || [cleaned];

        let index = 0;

        const speakNext = () => {
            if (index >= sentences.length) {
                // finished all sentences
                setTtsState({ status: "idle", messageId: null });
                return;
            }

            const utter = new SpeechSynthesisUtterance(
                sentences[index].trim()
            );

            // 🎛 Voice tuning – more natural / expressive
            utter.lang = "en-IN";
            utter.rate = 0.95;   // slightly slower = more natural
            utter.pitch = 1.08;  // a bit higher = more lively
            utter.volume = 1.0;

            // Try to pick a nice voice
            const voices = synth.getVoices();
            const preferredVoice =
                voices.find((v) => v.lang === "en-IN") ||
                voices.find((v) => v.lang.startsWith("en")) ||
                voices[0];
            if (preferredVoice) utter.voice = preferredVoice;

            utter.onstart = () => {
                if (index === 0) {
                    setTtsState({ status: "speaking", messageId });
                }
            };

            utter.onend = () => {
                index += 1;
                if (index < sentences.length) {
                    // small pause between sentences
                    setTimeout(speakNext, 120);
                } else {
                    setTtsState({ status: "idle", messageId: null });
                }
            };

            utter.onerror = () => {
                setTtsState({ status: "idle", messageId: null });
            };

            utter.onpause = () => {
                setTtsState((prev) => ({ ...prev, status: "paused" }));
            };

            utter.onresume = () => {
                setTtsState((prev) => ({ ...prev, status: "speaking" }));
            };

            synth.speak(utter);
        };

        speakNext();
    };


    const handleReadToggle = async (message) => {
        const currentAudio = audioRef.current;

        // 1️⃣ If clicking the SAME message → toggle pause / resume
        if (currentAudio && ttsState.messageId === message.id) {
            if (!currentAudio.paused && ttsState.status === "speaking") {
                // pause
                currentAudio.pause();
                setTtsState({ status: "paused", messageId: message.id });
            } else if (ttsState.status === "paused") {
                // resume
                try {
                    await currentAudio.play();
                    setTtsState({ status: "speaking", messageId: message.id });
                } catch (err) {
                    console.error("Resume play failed:", err);
                }
            }
            return;
        }

        // 2️⃣ Different message → stop old audio & cleanup URL
        if (currentAudio) {
            try {
                currentAudio.pause();
            } catch (e) {}
        }
        if (audioUrlRef.current) {
            try {
                URL.revokeObjectURL(audioUrlRef.current);
            } catch (e) {}
            audioUrlRef.current = null;
        }

        if (!message.text || !message.text.trim()) return;

        // 🔄 show loading state while waiting for TTS API
        setTtsState({ status: "loading", messageId: message.id });

        const formData = new FormData();
        formData.append("text", message.text);

        try {
            const res = await fetch(TTS_API_URL, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                console.error("TTS error:", await res.text());
                setTtsState({ status: "idle", messageId: null });
                return;
            }

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);

            audioRef.current = audio;
            audioUrlRef.current = url;

            audio.onended = () => {
                setTtsState((prev) =>
                    prev.messageId === message.id
                        ? { status: "idle", messageId: null }
                        : prev
                );
            };

            audio.onpause = () => {
                setTtsState((prev) =>
                    prev.messageId === message.id
                        ? { status: "paused", messageId: message.id }
                        : prev
                );
            };

            audio.onplay = () => {
                setTtsState({ status: "speaking", messageId: message.id });
            };

            await audio.play(); // this will trigger onplay → "speaking"
        } catch (err) {
            console.error("TTS fetch failed:", err);
            setTtsState({ status: "idle", messageId: null });
        }
    };





    const safeParseJSON = async (res) => {
        const txt = await res.text();
        try {
            return JSON.parse(txt);
        } catch {
            return { raw: txt };
        }
    };

    // ---- File / preview ----
    // ---- File / preview ----
    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(false);

        const file = e.dataTransfer.files && e.dataTransfer.files[0];
        if (!file) return;

        // only images allowed
        if (!file.type.startsWith("image/")) {
            alert("Please drop an image file (jpg, png, etc.)");
            return;
        }

        if (previewUrl) {
            try {
                URL.revokeObjectURL(previewUrl);
            } catch (err) {}
        }

        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
    };

    const handleFileSelected = (e) => {
        const f = e.target.files?.[0];
        if (!f) return;
        if (previewUrl) {
            try {
                URL.revokeObjectURL(previewUrl);
            } catch (e) {}
        }
        setSelectedFile(f);
        setPreviewUrl(URL.createObjectURL(f));
    };

    const clearImage = () => {
        setSelectedFile(null);
        if (previewUrl) {
            try {
                URL.revokeObjectURL(previewUrl);
            } catch (e) {}
            setPreviewUrl(null);
        }
        if (fileRef.current) fileRef.current.value = "";
        confirmedTranscriptRef.current = "";
        setUserInput("");
    };

    // ---- Network: XHR upload ----
    const uploadWithProgress = (file) => {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const form = new FormData();
            form.append("file", file);

            xhr.open("POST", "http://127.0.0.1:8000/chat", true);
            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable)
                    setUploadProgress(Math.round((e.loaded / e.total) * 100));
            };
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        resolve(JSON.parse(xhr.responseText));
                    } catch {
                        resolve({ raw: xhr.responseText });
                    }
                } else {
                    reject(
                        new Error(
                            "Upload failed: " + xhr.status + " - " + xhr.responseText
                        )
                    );
                }
            };
            xhr.onerror = () => reject(new Error("Network error during upload"));
            xhr.send(form);
        });
    };

    // ---- Voice Logic ----
    const createRecognizer = () => {
        if (!SpeechRecognition) return null;
        const rec = new SpeechRecognition();
        rec.lang = "en-IN";
        rec.continuous = true;
        rec.interimResults = true;
        rec.maxAlternatives = 1;
        rec._autoSendTimer = null;

        rec.onresult = (ev) => {
            let interim = "";
            let finalParts = [];
            for (let i = 0; i < ev.results.length; i++) {
                const r = ev.results[i];
                if (r.isFinal) {
                    try {
                        finalParts.push(r[0].transcript.trim());
                    } catch (e) {}
                } else {
                    try {
                        interim += (r[0].transcript || "").trim() + " ";
                    } catch (e) {}
                }
            }
            if (finalParts.length > 0) {
                confirmedTranscriptRef.current =
                    (confirmedTranscriptRef.current
                        ? confirmedTranscriptRef.current + " "
                        : "") + finalParts.join(" ");
            }
            const display =
                (confirmedTranscriptRef.current
                    ? confirmedTranscriptRef.current + (interim ? " " : "")
                    : "") + interim.trim();
            setUserInput(display);

            if (voiceMode) {
                if (rec._autoSendTimer) clearTimeout(rec._autoSendTimer);
                rec._autoSendTimer = setTimeout(() => {
                    if (
                        voiceMode &&
                        keepListeningRef.current &&
                        !isSendingRef.current &&
                        !loading
                    ) {
                        handleSendAnswer();
                    }
                }, 900);
            }
        };

        rec.onerror = (ev) => {
            console.warn("SpeechRecognition error event:", ev);
            const errName = ev?.error || "unknown";
            errorBackoffRef.current.lastError = errName;
            errorBackoffRef.current.count =
                (errorBackoffRef.current.count || 0) + 1;
            if (
                ["not-allowed", "service-not-allowed", "permission-denied"].includes(
                    errName
                )
            ) {
                pushMessage("agent", "⚠ Microphone access denied.");
                stopVoiceInput(true);
            }
        };

        rec.onend = () => {
            if (rec._autoSendTimer) {
                clearTimeout(rec._autoSendTimer);
                rec._autoSendTimer = null;
            }
            if (keepListeningRef.current) {
                const errors = errorBackoffRef.current.count || 0;
                let delay = 100;
                if (errors >= 1)
                    delay = Math.min(5000, 100 * Math.pow(2, Math.min(errors, 6)));

                const lastErr = errorBackoffRef.current.lastError;
                if (
                    ["not-allowed", "service-not-allowed", "permission-denied"].includes(
                        lastErr
                    )
                )
                    return;

                if (isRestartingRef.current) return;
                isRestartingRef.current = true;
                setTimeout(() => {
                    try {
                        if (!keepListeningRef.current) {
                            isRestartingRef.current = false;
                            return;
                        }
                        const newRec = createRecognizer();
                        if (newRec) {
                            recognitionRef.current = newRec;
                            newRec.start();
                            errorBackoffRef.current.count = 0;
                            setRecording(true);
                        }
                    } catch (e) {
                        console.warn(e);
                    } finally {
                        isRestartingRef.current = false;
                    }
                }, delay);
            } else {
                recognitionRef.current = null;
                setRecording(false);
            }
        };
        return rec;
    };

    const startVoiceInput = () => {
        if (!SpeechRecognition)
            return alert("Browser does not support SpeechRecognition.");
        if (keepListeningRef.current) return;
        keepListeningRef.current = true;
        const rec = createRecognizer();
        if (!rec) {
            keepListeningRef.current = false;
            return;
        }
        recognitionRef.current = rec;
        try {
            rec.start();
            setRecording(true);
        } catch (e) {
            console.warn(e);
            keepListeningRef.current = false;
            setRecording(false);
        }
    };

    const stopVoiceInput = (force = false) => {
        keepListeningRef.current = false;
        const rec = recognitionRef.current;
        if (rec) {
            try {
                rec.stop();
            } catch (e) {}
        }
        recognitionRef.current = null;
        isRestartingRef.current = false;
        setRecording(false);
    };

    const toggleVoiceMode = () => {
        const newMode = !voiceMode;
        setVoiceMode(newMode);
        if (newMode) {
            if (!keepListeningRef.current) startVoiceInput();
        } else {
            stopVoiceInput();
        }
    };

    // ---- Handlers ----
    const handleImageUpload = async () => {
        if (!selectedFile) return;
        if (loading || isSendingRef.current) return;

        stopVoiceInput();
        setLoading(true);
        isSendingRef.current = true;
        setUploadProgress(5);
        pushMessage("user", "Analyze this image 🌿");

        try {
            const data = await uploadWithProgress(selectedFile);
            setLastServerResponse(data);
            setUploadProgress(100);

            if (data?.ask_user) {
                pushMessage("agent", data.ask_user);
                // ❌ removed auto speak
                setConversationStarted(true);
            }

            if (data?.diagnosis) {
                pushMessage(
                    "agent",
                    `**Diagnosis:** ${data.diagnosis}\n\n**Remedy:** ${
                        data.remedy_text || "No specific remedy."
                    }`
                );
                // ❌ removed auto speak
                if (data.fertilizer_plan)
                    pushMessage(
                        "agent",
                        `**Fertilizer Plan:**\n${JSON.stringify(
                            data.fertilizer_plan,
                            null,
                            2
                        )}`
                    );
                setConversationStarted(false);
            }

            if (!data?.ask_user && !data?.diagnosis) {
                pushMessage("agent", data?.message ?? "Analysis complete.");
            }
        } catch (e) {
            console.error(e);
            pushMessage("agent", "⚠ Error uploading image.");
        } finally {
            setLoading(false);
            isSendingRef.current = false;
            setTimeout(() => setUploadProgress(0), 400);
            if (voiceMode && !recognitionRef.current) startVoiceInput();
        }
    };

    const handleSendAnswer = async () => {
        const trimmed = userInput.trim();
        if (!trimmed) return;
        if (loading || isSendingRef.current) return;

        stopVoiceInput();
        pushMessage("user", trimmed);
        setLoading(true);
        isSendingRef.current = true;
        setUploadProgress(5);
        setUserInput("");
        confirmedTranscriptRef.current = "";

        try {
            if (fetchControllerRef.current) fetchControllerRef.current.abort();
            fetchControllerRef.current = new AbortController();

            const form = new FormData();
            form.append("user_answer", trimmed);

            const res = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                body: form,
                signal: fetchControllerRef.current.signal,
            });

            if (!res.ok) throw new Error("Request failed");

            const data = await res.json();
            setLastServerResponse(data);
            setUploadProgress(100);

            if (data?.ask_user) {
                pushMessage("agent", data.ask_user);
                // ❌ removed auto speak
            } else if (data?.diagnosis) {
                pushMessage(
                    "agent",
                    `**Diagnosis:** ${data.diagnosis}\n\n**Remedy:** ${data.remedy_text}`
                );
                // ❌ removed auto speak
                if (data.fertilizer_plan)
                    pushMessage(
                        "agent",
                        `**Fertilizer:** ${JSON.stringify(data.fertilizer_plan)}`
                    );
                setConversationStarted(false);
            } else {
                pushMessage("agent", data?.message || "Received.");
            }
        } catch (e) {
            if (e.name !== "AbortError")
                pushMessage("agent", "⚠ I couldn't reach the server.");
        } finally {
            setLoading(false);
            isSendingRef.current = false;
            setTimeout(() => setUploadProgress(0), 400);
            if (voiceMode && !recognitionRef.current) startVoiceInput();
        }
    };

    const startNewConversation = async () => {
        setMessages([]);
        confirmedTranscriptRef.current = "";
        setUserInput("");
        stopVoiceInput();
        clearImage();
        setConversationStarted(false);
        setLastServerResponse(null);

        // 🔁 Tell backend to reset agent state
        try {
            await fetch("http://127.0.0.1:8000/reset", {
                method: "POST",
            });
        } catch (e) {
            console.warn("Failed to reset server conversation:", e);
        }
    };


    // --- Render ---
    return (
        <div className="app-container">
            {/* SIDEBAR */}
            <aside className="sidebar">
                <div className="brand">
                    <div className="logo-icon">
                        <IconPlant />
                    </div>
                    <span>Nutrient AI</span>
                </div>

                <div className="sidebar-content">
                    <div className="sidebar-section">
                        <h3 className="section-title">Context Image</h3>
                        <div
                            className={`upload-area drop-zone ${isDragOver ? "drag-over" : ""}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                        >
                            <input
                                ref={fileRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelected}
                                id="file-upload"
                                hidden
                            />

                            {!previewUrl ? (
                                <label htmlFor="file-upload" className="upload-placeholder">
                                    <IconPlus />
                                    <span>Add Plant Photo</span>
                                    <span className="upload-hint">Drag & drop or click</span>
                                </label>
                            ) : (
                                <div className="image-preview-wrapper">
                                    <img src={previewUrl} alt="Context" />
                                    <button className="remove-img-btn" onClick={clearImage}>
                                        ×
                                    </button>
                                </div>
                            )}

                            {selectedFile && !loading && !conversationStarted && (
                                <button className="analyze-btn" onClick={handleImageUpload}>
                                    Start Analysis
                                </button>
                            )}
                        </div>

                    </div>

                    <div className="sidebar-section spacer">{/* Spacer */}</div>

                    <div className="sidebar-footer">
                        <button
                            className={`mode-toggle ${voiceMode ? "active" : ""}`}
                            onClick={toggleVoiceMode}
                        >
                            <IconMic active={voiceMode} />
                            <span>{voiceMode ? "Voice Active" : "Voice Off"}</span>
                        </button>
                        <button className="new-chat-btn" onClick={startNewConversation}>
                            <IconRefresh /> New Chat
                        </button>
                    </div>
                </div>
            </aside>

            {/* MAIN CHAT AREA */}
            <main className="main-chat">
                {uploadProgress > 0 && uploadProgress < 100 && (
                    <div className="loading-bar-container">
                        <div
                            className="loading-bar"
                            style={{ width: `${uploadProgress}%` }}
                        ></div>
                    </div>
                )}

                <div className="chat-history" ref={chatHistoryRef}>
                    {messages.length === 0 ? (
                        <div className="welcome-screen">
                            <div className="hero-icon">
                                <IconPlant />
                            </div>
                            <h1>Hello, Gardener.</h1>
                            <p>
                                Upload a photo of your plant to diagnose nutrient deficiencies
                                or diseases.
                            </p>
                            <div className="suggestion-chips">
                                <button onClick={() => fileRef.current?.click()}>
                                    Upload Photo
                                </button>
                                <button onClick={toggleVoiceMode}>Start Voice Mode</button>
                            </div>
                        </div>
                    ) : (
                        messages.map((m) => (
                                <div key={m.id} className={`message-row ${m.role}`}>
                                    {m.role === "agent" && (
                                        <div className="avatar agent-avatar">
                                            <IconBot />
                                        </div>
                                    )}

                                    <div className="message-content">
                                        <div className="bubble">
                                            {m.text.split("**").map((part, i) =>
                                                i % 2 === 1 ? <strong key={i}>{part}</strong> : part
                                            )}
                                        </div>

                                        {m.role === "agent" && m.text && (
                                            <p
                                                className="read-bar"
                                                onClick={() => handleReadToggle(m)}
                                            >
                                                {ttsState.messageId === m.id && ttsState.status === "loading" ? (
                                                    <>
                                                        {/* ⏳ Loading dotted circle while TTS API is working */}
                                                        <span className="loading-spinner" />
                                                        <span className="read-bar-text">Loading…</span>
                                                    </>
                                                ) : ttsState.messageId === m.id && ttsState.status === "speaking" ? (
                                                    <>
                                                        {/* ⏸ followed by Pause */}
                                                        <span className="read-bar-icon">⏸</span>
                                                        <span className="read-bar-text">Pause</span>
                                                    </>
                                                ) : ttsState.messageId === m.id && ttsState.status === "paused" ? (
                                                    <>
                                                        {/* ▶ followed by Resume */}
                                                        <span className="read-bar-icon">▶</span>
                                                        <span className="read-bar-text">Resume</span>
                                                    </>
                                                ) : (
                                                    <>
                                                        {/* 🔊 followed by Read aloud (default) */}
                                                        <span className="read-bar-icon">🔊</span>
                                                        <span className="read-bar-text">Read aloud</span>
                                                    </>
                                                )}
                                            </p>
                                        )}

                                    </div>

                                    {m.role === "user" && (
                                        <div className="avatar user-avatar">You</div>
                                    )}
                                </div>
                            ))

                    )}
                    {loading && (
                        <div className="message-row agent">
                            <div className="avatar agent-avatar">
                                <IconBot />
                            </div>
                            <div className="typing-indicator">
                                <span>.</span>
                                <span>.</span>
                                <span>.</span>
                            </div>
                        </div>
                    )}
                    {/* Spacer to make room for the input dock */}
                    <div style={{ height: 120 }} />
                </div>

                {/* FLOATING INPUT CAPSULE */}
                <div className="input-dock">
                    <div
                        className={`input-capsule ${recording ? "recording-pulse" : ""}`}
                    >
                        <button
                            className="icon-btn"
                            onClick={() => fileRef.current?.click()}
                            title="Add Image"
                        >
                            <IconImage />
                        </button>

                        <input
                            ref={inputRef}
                            type="text"
                            placeholder={recording ? "Listening..." : "Ask follow-up questions..."}
                            value={userInput}
                            onChange={(e) => {
                                setUserInput(e.target.value);
                                confirmedTranscriptRef.current = e.target.value;
                            }}
                            onKeyDown={(e) => e.key === "Enter" && handleSendAnswer()}
                            disabled={loading}
                        />

                        {userInput.trim() ? (
                            <button className="icon-btn send-btn" onClick={handleSendAnswer}>
                                <IconSend />
                            </button>
                        ) : (
                            <button
                                className={`icon-btn mic-btn ${recording ? "active" : ""}`}
                                onClick={
                                    recording ? () => stopVoiceInput(false) : startVoiceInput
                                }
                            >
                                <IconMic active={recording} />
                            </button>
                        )}
                    </div>
                    <div className="footer-note">
                        AI can make mistakes. Check important info.
                    </div>
                </div>
            </main>
        </div>
    );
}

