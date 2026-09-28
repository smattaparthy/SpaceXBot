import Image from "next/image";

export default function NavBar() {
  return (
    <nav className="navbar">
      <Image
        src="/images/spaceXLogo.webp"
        alt="SpaceX"
        width={140}
        height={40}
      />

      <span>VEHICLES</span>
    </nav>
  );
}