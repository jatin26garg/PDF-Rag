import { Mr_Bedfort } from 'next/font/google';
import { 
    uploadDocument, 
    getDocuments, 
    deleteDocument, 
    queryRAG, 
    queryRAGStream 
} from './api';
import {Document, UploadResponse, QueryRequest, QueryResponse} from '@/src/types'

const MAX_FILE_SIZE = 10*1024*1024;

const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
];

const ALLOWED_EXTENTIONS = ['.pdf', '.docx' , '.txt'];

export const ragService = {
    upload : async(file: File) : Promise<UploadResponse> =>{
        if(!file) throw new Error('NO file provided');
        const ext = '.'  + file.name.split('.').pop()?.toLowerCase();
        
        if(!ALLOWED_EXTENTIONS.includes(ext)){
            throw new Error(`File type ${ext}  not supported . please upload PDF ,DOCX, or TXT`);
        }
        if(file.size  > MAX_FILE_SIZE){
                throw new Error(`File size (${(file.size / 1024/1024).toFixed(1)}MB) exceds 10 MB limit`)
        }
        return await uploadDocument(file)
    },

    list : async () : Promise<Document[]> => {
        return await getDocuments();
    },

    delete :async (documentId : string): Promise<void> =>{
        await deleteDocument(documentId);
    },

    ask: async (question : string , top_k :number = 3) : Promise<QueryResponse>=>{
        if(!question.trim){
            throw new Error('Question cannot be empty');
        }
        return await queryRAG({question: question.trim(), top_k : top_k});
    },

    askStream : async(question:string, onChunk: (chunk : string)=>void,onComplete:()=>void, onError: (error: Error)=>void, top_k:number = 3)=>{
        if(!question.trim()){
            throw new Error('Question cannot be empty');
            return;
        }
        await queryRAGStream(
            {question: question.trim() , top_k : top_k},
            onChunk,
            onComplete,
            onError,
        );
    }
    
}