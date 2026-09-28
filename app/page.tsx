import ChatWidget from "./components/ChatWidget";
import NavBar from "./components/NavBar";

export default function Home() {
  return (
    <main className="hero">
      <NavBar />

      <div className="heroContent">
        <ChatWidget />
      </div>
    </main>
  );
}