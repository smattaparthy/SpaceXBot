import Image from "next/image";

interface NavBarProps {
  onNewChat?: () => void;
}

export default function NavBar({ onNewChat }: NavBarProps) {
  return (
    <header className="sticky top-0 z-10 bg-space">
      <div className="mx-auto flex h-16 w-full max-w-2xl items-center justify-between px-5 sm:px-6">
        <div className="flex items-center gap-3">
          {/* The logo file is 16:9 with a padded black field; crop to the wordmark. */}
          <div className="relative -mr-[12px] -ml-[15px] h-[28px] w-[168px] overflow-hidden">
            <Image
              src="/images/spaceXLogo.webp"
              alt="SpaceX"
              fill
              sizes="168px"
              preload
              className="object-cover"
            />
          </div>
          <span className="font-display text-lg font-medium text-silver">
            Mission Control
          </span>
        </div>

        {onNewChat && (
          <button
            type="button"
            onClick={onNewChat}
            className="font-display text-base font-medium text-silver hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-silver"
          >
            New chat
          </button>
        )}
      </div>
    </header>
  );
}
