var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
import { ApolloLink, } from 'apollo-link';
import { OperationQueuing } from './queuing';
export { OperationQueuing } from './queuing';
var throwServerError = function (response, result, message) {
    var error = new Error(message);
    error.response = response;
    error.statusCode = response.status;
    error.result = result;
    throw error;
};
var parseAndCheckResponse = function (operation, accessTokenField) { return function (response) {
    return response
        .text()
        .then(function (bodyText) {
        if (typeof bodyText !== 'string' || !bodyText.length) {
            return bodyText || '';
        }
        try {
            return JSON.parse(bodyText);
        }
        catch (err) {
            var parseError = err;
            parseError.response = response;
            parseError.statusCode = response.status;
            parseError.bodyText = bodyText;
            return Promise.reject(parseError);
        }
    })
        .then(function (parsedBody) {
        if (response.status >= 300) {
            throwServerError(response, parsedBody, "Response not successful: Received status code " + response.status);
        }
        if (!parsedBody.hasOwnProperty(accessTokenField)
            && (parsedBody.data && !parsedBody.data.hasOwnProperty(accessTokenField))
            && !parsedBody.hasOwnProperty('errors')) {
            throwServerError(response, parsedBody, "Server response was missing for query '" + operation.operationName + "'.");
        }
        return parsedBody;
    });
}; };
var TokenRefreshLink = (function (_super) {
    __extends(TokenRefreshLink, _super);
    function TokenRefreshLink(params) {
        var _this = _super.call(this) || this;
        _this.extractToken = function (body) {
            if (body.data) {
                return body.data[_this.accessTokenField];
            }
            return body[_this.accessTokenField];
        };
        _this.accessTokenField = (params && params.accessTokenField) || 'access_token';
        _this.fetching = false;
        _this.isTokenValidOrUndefined = params.isTokenValidOrUndefined;
        _this.fetchAccessToken = params.fetchAccessToken;
        _this.handleFetch = params.handleFetch;
        _this.handleResponse = params.handleResponse || parseAndCheckResponse;
        _this.handleError = typeof params.handleError === 'function'
            ? params.handleError
            : function (err) {
                console.error(err);
            };
        _this.queue = new OperationQueuing();
        return _this;
    }
    TokenRefreshLink.prototype.request = function (operation, forward) {
        var _this = this;
        if (typeof forward !== 'function') {
            throw new Error('[Token Refresh Link]: Token Refresh Link is non-terminating link and should not be the last in the composed chain');
        }
        if (this.isTokenValidOrUndefined()) {
            return forward(operation);
        }
        if (!this.fetching) {
            this.fetching = true;
            this.fetchAccessToken()
                .then(this.handleResponse(operation, this.accessTokenField))
                .then(function (body) {
                var token = _this.extractToken(body);
                if (!token) {
                    throw new Error('[Token Refresh Link]: Unable to retrieve new access token');
                }
                return token;
            })
                .then(this.handleFetch)
                .catch(this.handleError)
                .finally(function () {
                _this.fetching = false;
                _this.queue.consumeQueue();
            });
        }
        return this.queue.enqueueRequest({
            operation: operation,
            forward: forward,
        });
    };
    return TokenRefreshLink;
}(ApolloLink));
export { TokenRefreshLink };
//# sourceMappingURL=tokenRefreshLink.js.map