package com.binfinity.chatapp.controller;

import com.binfinity.chatapp.entity.Message;
import com.binfinity.chatapp.service.MessageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
@CrossOrigin(origins = "*") // 允许所有来源访问
@RestController
@RequestMapping("/chat")
@RequiredArgsConstructor
public class ChatController {
    private final MessageService messageService;

    @PostMapping("/send")
    public ResponseEntity<?> sendMessage(@RequestBody Map<String, String> request) {
        try {
            // 获取请求中的发送者、接收者和消息内容
            String sender = request.get("sender");
            String receiver = request.get("receiver");
            String content = request.get("content");

            // 调用服务层发送消息
            Message message = messageService.sendMessage(sender, receiver, content);

            // 返回成功响应
            return ResponseEntity.ok(Map.of("message", "消息发送成功", "content", message.getContent(), "timestamp", message.getTimestamp()));
        } catch (Exception e) {
            // 捕获异常并返回错误信息
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", e.getMessage()));
        }
    }

}
