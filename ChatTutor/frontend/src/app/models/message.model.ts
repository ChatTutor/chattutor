import { Paper } from "./paper.model";

export interface Message {
    from: string;
    message: string;
    date: Date;
    delay?: Number;
    papers?: Paper[];
}

export function asConversation(messages: Message[]) {
    let conversation:any[] = []
    messages.forEach(mess => {
      let contextdocs:any[] = []
      mess.papers?.forEach(paper => {
        contextdocs.push(paper)
      })
      conversation.push({
        "role" : mess.from,
        "content" : mess.message,
        "context_documents": contextdocs
      })
    })
    return conversation
}