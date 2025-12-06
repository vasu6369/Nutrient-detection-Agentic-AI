// import { useState } from "react";
// import axios from "axios";
// import { IoSend } from "react-icons/io5";
// import { MdOutlineDarkMode, MdOutlineLightMode } from "react-icons/md";
// import { FaMicrophone } from "react-icons/fa";

// export default function ChatBot() {
//   const [messages, setMessages] = useState([
//     {
//       from: "bot",
//       text: "Vanakkam! 👋 I am your farming assistant. You can upload a banana leaf image or just start chatting.",
//     },
//   ]);
//   const [userText, setUserText] = useState("");
//   const [imageFile, setImageFile] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [dark, setDark] = useState(true); // default dark

//   const handleSend = async () => {
//     if (!userText && !imageFile) return;

//     const formData = new FormData();
//     if (imageFile) formData.append("file", imageFile);
//     if (userText) formData.append("user_answer", userText);

//     // show user message in chat
//     setMessages((prev) => [
//       ...prev,
//       { from: "user", text: userText || "📷 Sent an image for diagnosis" },
//     ]);

//     setUserText("");
//     setImageFile(null);
//     setLoading(true);

//     try {
//       const res = await axios.post("http://127.0.0.1:8000/chat", formData);
//       const data = res.data;

//       // Case 1: Agent is still asking questions
//       if (data.ask_user) {
//         setMessages((prev) => [
//           ...prev,
//           { from: "bot", text: data.ask_user },
//         ]);
//       } else {
//         // Case 2: Final response with diagnosis + remedy + fertilizer
//         if (data.diagnosis) {
//           setMessages((prev) => [
//             ...prev,
//             {
//               from: "bot",
//               text: `🌿 Diagnosis: ${data.diagnosis}`,
//             },
//           ]);
//         }

//         if (data.remedy_text) {
//           setMessages((prev) => [
//             ...prev,
//             {
//               from: "bot",
//               text: `🧪 Remedy:\n${data.remedy_text}`,
//             },
//           ]);
//         }

//         if (data.fertilizer_plan) {
//           const fertJson =
//             typeof data.fertilizer_plan === "string"
//               ? data.fertilizer_plan
//               : JSON.stringify(data.fertilizer_plan, null, 2);

//           setMessages((prev) => [
//             ...prev,
//             {
//               from: "bot",
//               text: `🧂 Fertilizer Plan:\n${fertJson}`,
//             },
//           ]);
//         }

//         // Optional: if you add llm_reply later:
//         if (data.llm_reply) {
//           setMessages((prev) => [
//             ...prev,
//             { from: "bot", text: data.llm_reply },
//           ]);
//         }
//       }
//     } catch (err) {
//       console.error(err);
//       setMessages((prev) => [
//         ...prev,
//         {
//           from: "bot",
//           text: "⚠️ I had trouble reaching the server. Please check if the backend is running.",
//         },
//       ]);
//     }

//     setLoading(false);
//   };

//   const handleKeyDown = (e) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       handleSend();
//     }
//   };

//   const toggleTheme = () => {
//     setDark((prev) => !prev);
//   };

//   return (
//     <div className={dark ? "dark h-screen" : "h-screen"}>
//       <div className="h-full flex items-center justify-center bg-slate-100 dark:bg-slate-900 transition-colors">
//         <div className="w-full max-w-3xl h-[90vh] flex flex-col border border-slate-300 dark:border-slate-700 rounded-2xl shadow-xl bg-white dark:bg-slate-800 overflow-hidden">
//           {/* Header */}
//           <header className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
//             <div>
//               <h1 className="text-lg font-semibold flex items-center gap-2 text-slate-900 dark:text-slate-50">
//                 🌾 Farm AI Agent
//               </h1>
//               <p className="text-xs text-slate-500 dark:text-slate-400">
//                 Upload leaf images, answer questions, and get nutrient & fertilizer guidance.
//               </p>
//             </div>

//             <button
//               onClick={toggleTheme}
//               className="p-2 rounded-full border border-slate-300 dark:border-slate-600 hover:bg-slate-200 dark:hover:bg-slate-700"
//             >
//               {dark ? (
//                 <MdOutlineLightMode className="text-yellow-300" size={20} />
//               ) : (
//                 <MdOutlineDarkMode className="text-slate-800" size={20} />
//               )}
//             </button>
//           </header>

//           {/* Messages */}
//           <main className="flex-1 overflow-y-auto px-4 py-3 space-y-2 bg-slate-50 dark:bg-slate-900">
//             {messages.map((msg, idx) => (
//               <div
//                 key={idx}
//                 className={`flex ${
//                   msg.from === "user" ? "justify-end" : "justify-start"
//                 }`}
//               >
//                 <div
//                   className={`max-w-[80%] whitespace-pre-wrap px-3 py-2 rounded-2xl text-sm
//                   ${
//                     msg.from === "user"
//                       ? "bg-emerald-600 text-white rounded-br-sm"
//                       : "bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-50 rounded-bl-sm"
//                   }`}
//                 >
//                   {msg.text}
//                 </div>
//               </div>
//             ))}

//             {loading && (
//               <div className="flex justify-start">
//                 <div className="px-3 py-2 text-sm rounded-2xl bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 animate-pulse">
//                   🤖 Thinking…
//                 </div>
//               </div>
//             )}
//           </main>

//           {/* Bottom input area */}
//           <footer className="border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-3">
//             {/* Image preview row */}
//             {imageFile && (
//               <div className="mb-2 text-xs text-slate-600 dark:text-slate-300 flex items-center justify-between">
//                 <span>📷 Image selected: {imageFile.name}</span>
//                 <button
//                   onClick={() => setImageFile(null)}
//                   className="text-red-500 hover:underline"
//                 >
//                   remove
//                 </button>
//               </div>
//             )}

//             <div className="flex items-center gap-2">
//               {/* File input */}
//               <label className="text-xs cursor-pointer px-2 py-1 border border-dashed border-emerald-500 rounded-lg text-emerald-600 hover:bg-emerald-50 dark:hover:bg-slate-800">
//                 📎 Leaf Image
//                 <input
//                   type="file"
//                   accept="image/*"
//                   className="hidden"
//                   onChange={(e) => {
//                     if (e.target.files && e.target.files[0]) {
//                       setImageFile(e.target.files[0]);
//                     }
//                   }}
//                 />
//               </label>

//               {/* Voice placeholder (future hook) */}
//               <button
//                 className="p-2 rounded-full border border-slate-300 dark:border-slate-600 text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
//                 disabled
//                 title="Voice input coming soon"
//               >
//                 <FaMicrophone size={16} />
//               </button>

//               {/* Text input */}
//               <textarea
//                 rows={1}
//                 className="flex-1 resize-none text-sm px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
//                 placeholder="Type your answer or question…"
//                 value={userText}
//                 onChange={(e) => setUserText(e.target.value)}
//                 onKeyDown={handleKeyDown}
//               />

//               {/* Send button */}
//               <button
//                 onClick={handleSend}
//                 disabled={loading}
//                 className="p-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-60 disabled:cursor-not-allowed"
//               >
//                 <IoSend size={20} />
//               </button>
//             </div>

//             <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500 text-right">
//               Model: Local LLM + CV + RAG + Fertilizer engine
//             </p>
//           </footer>
//         </div>
//       </div>
//     </div>
//   );
// }
