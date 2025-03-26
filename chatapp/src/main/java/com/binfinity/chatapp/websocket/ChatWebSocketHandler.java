package com.binfinity.chatapp.websocket;

import com.binfinity.chatapp.entity.Message;
import com.binfinity.chatapp.service.MessageService;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
@RequiredArgsConstructor
public class ChatWebSocketHandler extends TextWebSocketHandler {
    private final MessageService messageService;
    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.put(session.getId(), session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String payload = message.getPayload();
        Map<String, String> data = new ObjectMapper().readValue(payload, Map.class);

        String sender = data.get("sender");
        String receiver = data.get("receiver");
        String content = data.get("content");

        Message savedMessage = messageService.sendMessage(sender, receiver, content);

        for (WebSocketSession s : sessions.values()) {
            s.sendMessage(new TextMessage(new ObjectMapper().writeValueAsString(savedMessage)));
        }
    }
}
