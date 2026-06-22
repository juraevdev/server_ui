"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { Messages, Message } from "./Messages";

type PanelLayoutProps = {
  title: string;
  heading: string;
  messages?: Message[];
  headerActions?: ReactNode;
  children: ReactNode;
};

export function PanelLayout({
  title,
  heading,
  messages = [],
  headerActions,
  children,
}: PanelLayoutProps) {
  return (
    <div className="wrap">
      <header>
        <h1>{heading}</h1>
        <div className="btn-group header-actions">
          {headerActions ?? (
            <>
              <Link className="btn" href="/">
                Dashboard
              </Link>
              <Link className="btn" href="/images/create">
                Create image
              </Link>
              <Link className="btn btn-primary" href="/create">
                Create container
              </Link>
            </>
          )}
        </div>
      </header>

      <Messages messages={messages} />
      {children}
    </div>
  );
}
