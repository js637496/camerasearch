import { ApolloLink, Observable, Operation, NextLink, FetchResult } from 'apollo-link';
export { OperationQueuing, QueuedRequest } from './queuing';
export declare type FetchAccessToken = (...args: any[]) => Promise<Response>;
export declare type HandleFetch = (accessToken: string) => void;
export declare type HandleResponse = (operation: Operation, accessTokenField: string) => any;
export declare type HandleError = (err: Error) => void;
export declare type IsTokenValidOrUndefined = (...args: any[]) => boolean;
export declare class TokenRefreshLink extends ApolloLink {
    private accessTokenField;
    private fetching;
    private isTokenValidOrUndefined;
    private fetchAccessToken;
    private handleFetch;
    private handleResponse;
    private handleError;
    private queue;
    constructor(params: {
        accessTokenField?: string;
        isTokenValidOrUndefined: IsTokenValidOrUndefined;
        fetchAccessToken: FetchAccessToken;
        handleFetch: HandleFetch;
        handleResponse?: HandleResponse;
        handleError?: HandleError;
    });
    request(operation: Operation, forward: NextLink): Observable<FetchResult>;
    private extractToken;
}
