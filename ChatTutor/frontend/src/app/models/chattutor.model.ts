import {Message} from "./message.model";

export interface ChatTutor {
    conversation: Message[],
    multiple: boolean,
    collection?: string[] | ['test_embedding']
    from_doc?: string
}