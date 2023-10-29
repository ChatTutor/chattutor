import { Paper } from "./paper.model";

export interface Message {
    sender: 'Student' | 'Assistant',
    timestamp: string,
    role: 'user' | 'assistant',
    content: string,
    delay?: Number,
    valid_docs?: any[],
    chat_k?: string,
    clear_number?: string,
    time_created?: string,
}

export interface DataMessage {
    message: Message,
}

export function asConversation(messages: Message[]) {
    let conversation:any[] = []
    messages.forEach(mess => {
      let contextdocs:any[] = []
      mess.valid_docs?.forEach(paper => {
        contextdocs.push(paper)
      })
      conversation.push({
        "role" : mess.role,
        "content" : mess.content,
        "context_documents": contextdocs
      })
    })
    return conversation
}