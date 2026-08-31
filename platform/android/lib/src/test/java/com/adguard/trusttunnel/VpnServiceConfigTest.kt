package com.adguard.trusttunnel

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test

class VpnServiceConfigTest {
    @Test
    fun parseToml_readsApplicationSplitTunnelLists() {
        val config = VpnServiceConfig.parseToml(
            """
            dns_upstreams = []

            [listener.tun]
            included_routes = ["0.0.0.0/0"]
            excluded_routes = ["10.0.0.0/8"]
            disallowed_applications = [" com.android.chrome ", "org.mozilla.firefox", "com.android.chrome"]
            allowed_applications = ["com.securesoft.only"]
            mtu_size = 1500
            """.trimIndent()
        )

        assertNotNull(config)
        assertEquals(
            listOf(" com.android.chrome ", "org.mozilla.firefox", "com.android.chrome"),
            config!!.listener.tun.disallowedApplications
        )
        assertEquals(listOf("com.securesoft.only"), config.listener.tun.allowedApplications)
    }
}
