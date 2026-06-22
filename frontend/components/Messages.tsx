export type Message = {
  type: "success" | "error";
  text: string;
};

type MessagesProps = {
  messages: Message[];
};

export function Messages({ messages }: MessagesProps) {
  if (!messages.length) return null;

  return (
    <ul className="messages">
      {messages.map((message, index) => (
        <li key={index} className={message.type}>
          {message.text}
        </li>
      ))}
    </ul>
  );
}
