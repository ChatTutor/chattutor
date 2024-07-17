import {Message} from "./message.model";

export interface ChatTutor {
    conversation: Message[],
    selectedModel:  "gpt-3.5-turbo-16k" | "gpt-3.5-turbo-8k" | "gpt-4o",
    multiple: boolean,
    collection?: string[] | ['test_embedding']
    from_doc?: string
    credential_token?: string,
    response_type?: string
}