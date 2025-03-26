package com.binfinity.chatapp.config;

import org.springframework.stereotype.Component;

import java.util.Date;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;


@Component  // 确保 Spring 能够管理这个类
public class JwtUtil {
    private final String SECRET_KEY = "X0t/f0jC90+98GdXDlqJI5uVnQAkqXBmOEfzRuGVRJE=";

    public String generateToken(String username) {
        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 10)) // 10小时有效
                .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
                .compact();
    }



    public String extractUsername(String token) {
        return Jwts.parser()
                .setSigningKey(SECRET_KEY)
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }
}
