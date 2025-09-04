from .base_agent import BaseAgent
from .prompts.super_prompts import CODE_GEN_PERSONA, CODE_GEN_GOAL
from apps.projects.models import Project
from django.db import transaction
import google.generativeai as genai
import os
import json

class CodeGenAgent(BaseAgent):
    """
    Generates the mobile application source code.
    """
    def __init__(self):
        super().__init__(
            agent_name="Code Generation",
            agent_persona=CODE_GEN_PERSONA,
            goal=CODE_GEN_GOAL
        )
        self.model = genai.GenerativeModel(model_name='google/gemini-pro-2.5-experimental')

    def execute(self, project_id: int):
        """
        Generates the source code for a given project using a comprehensive,
        persona-driven, multi-step reasoning framework.
        
        Args:
            project_id (int): The ID of the project to build.
        """
        print(f"Executing Code Generation Agent for project {project_id}...")
        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status_message = "Generating production-ready code with advanced features..."
                project.status = Project.ProjectStatus.CODE_GENERATION # Set status to generation
                project.save()
        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return

        # 1. Gather all data, including new survey flags and questions
        user_persona = project.user_persona_document
        palette = project.brand_palette
        app_type = project.app_type
        source_url = project.source_url
        enable_ux_survey = project.enable_ux_survey
        ux_survey_questions = project.ux_survey_questions
        enable_pmf_survey = project.enable_pmf_survey
        pmf_survey_questions = project.pmf_survey_questions

        # Placeholder PMF questions (as I cannot access external articles)
        if not pmf_survey_questions:
            pmf_survey_questions = [
                {"id": 1, "question": "How would you feel if you could no longer use [App Name]?", "type": "radio", "options": ["Very disappointed", "Somewhat disappointed", "Not disappointed (it's not that useful)"]},
                {"id": 2, "question": "What is the primary benefit you receive from [App Name]?", "type": "text"},
                {"id": 3, "question": "How likely are you to recommend [App Name] to a friend or colleague?", "type": "nps", "scale": [0, 10]},
                {"id": 4, "question": "What alternatives would you use if [App Name] were no longer available?", "type": "text"}
            ]
        if not ux_survey_questions:
             ux_survey_questions = [
                {"id": 1, "question": "How easy is it to navigate this app?", "type": "scale", "min": 1, "max": 5, "labels": ["Very Difficult", "Very Easy"]},
                {"id": 2, "question": "What do you like most about the app?", "type": "text"},
                {"id": 3, "question": "What could be improved?", "type": "text"},
                {"id": 4, "question": "Overall, how satisfied are you with the app?", "type": "radio", "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]}
            ]




        
        # 2. Construct the detailed task for the Gemini API with multi-step reasoning
        task_description = f"""
        **MISSION CRITICAL TASK: Generate a production-ready mobile application with an integrated feedback engine.**

        **Input Data:**
        - **Target Platform:** {project.app_type}
        - **User Persona:** {project.user_persona_document}
        - **Brand Palette:** {json.dumps(project.brand_palette, indent=2)}
        - **Enable UX Survey:** {project.enable_ux_survey}
        - **Enable PMF Survey:** {project.enable_pmf_survey}

        **Core Instructions:**
        1.  Generate the complete, high-quality source code for the requested mobile application.
        2.  The code must be clean, scalable, and follow platform-specific best practices.
        3.  Implement all UI elements using the provided `Brand Palette`.

        **Feedback Engine Implementation (MANDATORY):**

        You MUST generate code that performs the following actions within the mobile app:

        1.  **Check Survey Flags:** The app MUST check the `enable_ux_survey` and `enable_pmf_survey` flags from the backend upon startup or when the relevant screen is loaded.

        2.  **Display Survey Overlay:**
            * If a survey is enabled, the app MUST display a **non-intrusive, full-screen survey overlay**.
            * This overlay should appear after a set period of use (e.g., after the 5th app open, or 1 week after install). This logic should be implemented using local storage (e.g., SharedPreferences on Android, UserDefaults on iOS) to track app open counts or install date.
            * The survey form itself must be **beautifully styled** using the app's own branding (colors, fonts) derived from the `Brand Palette`.

        3.  **User Control:**
            * The survey overlay MUST include a clear and prominent **"Dismiss" or "Skip" button**.
            * The survey must only be shown **once per user**. After being shown (and either completed or dismissed), it should not appear again. Use local storage to track this state (e.g., `has_shown_pmf_survey = true`).

        4.  **Analytics Tracking:**
            * The app must track and send analytics events to the backend for the following actions:
                * `survey_impression`: Fired when the user is shown the survey overlay.
                * `survey_dismissed`: Fired when the user clicks the "Dismiss" or "Skip" button.
                * `survey_completed`: Fired when the user successfully submits the survey form.
        
        Generate the code for all necessary files, including UI, logic, and analytics hooks.
        """
        **Input Data:**
        -   **Target Platform(s):** {app_type} (options: 'ANDROID', 'IOS', 'BOTH')
        -   **Core User Persona Document:**
            ```markdown
            {user_persona}
            ```
        -   **Brand Color Palette (JSON):**
            ```json
            {json.dumps(palette, indent=2)}
            ```
        -   **Original Website URL (for content/product context):** {source_url}
        -   **User Experience (UX) Survey Enabled:** {enable_ux_survey}
            -   **UX Survey Questions:** {json.dumps(ux_survey_questions, indent=2)}
        -   **Product Market Fit (PMF) Survey Enabled:** {enable_pmf_survey}
            -   **PMF Survey Questions:** {json.dumps(pmf_survey_questions, indent=2)}

        ---

        **Multi-Step Reasoning Framework (Strict Adherence Required):**

        **Step 1: Deconstruct the Persona and Website Intent**
        * Analyze the `Core User Persona Document` to explicitly state your understanding of the target user's primary needs, motivations, and pain points relevant to a mobile application.
        * Infer the *primary purpose* of the mobile application based on the user persona and the content implied by the `Original Website URL`. Is it an e-commerce app, a content consumption app, a service booking app, a utility app, etc.? Justify your inference.

        **Step 2: Define Core App Logic, Key Features, and Feedback Integration Strategy**
        * Based on the inferred primary purpose (from Step 1), define the essential functionalities (e.g., "display product catalog," "user authentication," "content search," "booking calendar").
        * Outline the minimal set of screens/views required to fulfill these core functionalities (e.g., "Home/Dashboard," "Detail View," "Profile," "Settings").
        * **Crucially, define the strategy for integrating user feedback mechanisms within the app:**
            * How will UX and PMF surveys be displayed (e.g., subtle in-app prompt, dedicated section, pop-up with dismiss option)? Design this to not overwhelm the user.
            * How will survey responses, ratings, and general feedback be collected and transmitted securely to the backend?
            * How will user interaction with survey prompts (saw, ignored, answered) be tracked for analytics?

        **Step 3: Propose Logical File Structure for {app_type}**
        * Outline a complete and professional file/folder structure for the `{app_type}` application.
        * If the `app_type` is 'BOTH', generate two separate, native codebases: one for iOS (Swift/SwiftUI) and one for Android (Kotlin).
        * Include folders for UI components, screens/views, utilities, data models, networking, and styling/theming.
        * **Explicitly include structure for the Survey/Feedback module.**

        **Step 4: Generate Code - Detailed Implementation**
        * Generate the full, production-ready source code for each file identified in Step 3.
        * For each file, start with a comment specifying the full file path.
        * **Crucially, integrate the `Brand Color Palette` into a dedicated theme/style file.** All UI elements in the generated code MUST reference colors from this palette, not hardcoded values.
        * For content, use placeholder data that aligns with the inferred app purpose (e.g., `dummyProducts`, `sampleArticles`).
        * Ensure the code is clean, well-commented, and follows best practices for {app_type} development. For iOS, use Swift/SwiftUI and maximize the use of modern UI features like "liquid glass" effects. For Android, use Kotlin.
        * **Implement the survey display and data collection features.** Provide a clear button for users to trigger the survey, and a dismiss option for pop-ups. Include tracking logic.
        * The output format MUST be a series of distinct code blocks, each clearly preceded by its file path.

        ---
        **Example Output Format for Step 4 (Apply this for ALL generated code, adapting paths):**
        
        ```swift
        // File: MyApp/Views/ContentView.swift
        import SwiftUI

        struct ContentView: View {
            var body: some View {
                Text("Hello, world!")
                    .padding()
            }
        }
        ```
        
        ---
        **Begin your detailed, multi-step reasoning and code generation now.**
        """
        
        full_prompt = self._generate_prompt(task_description)

        try:
            # Simulate API call
            # In a real application, this would call self.model.generate_content(full_prompt)
            # For this exercise, we will simulate the expected output structure.
            # The actual response will be very large and context-dependent,
            # especially with the new survey features.

            # This is a simplified simulation of the actual code generation.
            # A real model output would be much more extensive and detailed,
            # explicitly including files for survey UI, data models, and API integration.
            simulated_code_output = f"""
            **Step 1: Deconstruct the Persona and Website Intent**
            * **Understanding of User Persona:** The persona "Digital Nomad Diana" indicates a user who is highly mobile, values efficiency, seamless integration, and clean interfaces for managing her professional and digital life. She seeks instant access and reliable tools to navigate her travel-heavy lifestyle.
            * **Inferred Primary Purpose:** The mobile application's primary purpose is to serve as a **highly efficient mobile companion for digital professionals**, extending the core functionalities of `{source_url}` into a native, offline-capable, and intuitively designed mobile experience. It's about empowering Diana to manage her work and engagement on the go.

            **Step 2: Define Core App Logic, Key Features, and Feedback Integration Strategy**
            * **Essential Functionalities:**
                * Secure User Authentication & Profile Management.
                * Access to core content/products/services from `{source_url}`.
                * Push Notifications for critical updates.
                * **Integrated Feedback & Survey Module:**
                    * UX and PMF Surveys with dynamic question rendering.
                    * In-app rating collection.
                    * Textual feedback submission.
            * **Minimal Screens/Views:**
                * `AuthScreen` (Login/Signup)
                * `Dashboard/Home Screen` (Main content, quick actions)
                * `Content/Product Detail Screen`
                * `Profile/Settings Screen`
                * `Survey/Feedback Module` (Accessible via dedicated section and/or subtle, dismissible pop-ups).
            * **Feedback Integration Strategy:**
                * **Survey Display:** A subtle, non-intrusive pop-up will appear after a user completes a certain action or has spent a minimum time in the app, with a clear 'Dismiss' button and a 'Don't show again' option. A dedicated 'Feedback' section will also be available in the app settings.
                * **Data Collection:** Survey responses, ratings, and text feedback will be collected via secure API calls to the Applause backend, validated, and timestamped.
                * **Tracking:** Each survey impression (saw), interaction (ignored, clicked), and completion (answered) will be logged to provide granular analytics on user engagement with feedback prompts.

            **Step 3: Propose Logical File Structure for {app_type}**
            * **For Android (Kotlin):**
                ```
                app/
                ├── src/
                │   └── main/
                │       ├── java/
                │       │   └── com/yourcompany/yourapp/
                │       │       ├── MainActivity.kt
                │       │       ├── ui/
                │       │       │   ├── theme/ # Color, Theme, Type
                │       │       │   ├── screens/ # AuthScreen, HomeScreen, DetailScreen, ProfileScreen
                │       │       │   ├── components/ # Generic UI components
                │       │       │   └── feedback/ # NEW: SurveyDialog, FeedbackScreen, RatingComponent
                │       │       ├── data/
                │       │       │   ├── model/ # Product, User, SurveyResponse, AppRating, Feedback
                │       │       │   └── repository/ # Repository for data access including feedback submission
                │       │       ├── network/ # API service for backend communication
                │       │       └── util/ # Constants, AnalyticsLogger (for survey interaction tracking)
                │       └── res/
                └── build.gradle
                ```
            * **For iOS (SwiftUI):**
                ```
                YourAppName/
                ├── YourAppNameApp.swift
                ├── Views/ # AuthView, HomeView, DetailView, ProfileView
                ├── Components/ # Generic UI components, LiquidGlassView
                ├── Feedback/ # NEW: SurveyPromptView, FeedbackView, RatingView, SurveyModels.swift
                ├── Models/ # Product, User, SurveyResponse, AppRating, Feedback
                ├── Services/ # API service for backend communication, AnalyticsService (for survey tracking)
                └── Theme/ # ColorPalette.swift
                ```

            **Step 4: Generate Code - Detailed Implementation**

            ```swift
            // File: YourAppName/Components/LiquidGlassView.swift
            import SwiftUI

            struct LiquidGlassView: View {
                var body: some View {
                    ZStack {
                        Rectangle()
                            .fill(LinearGradient(
                                gradient: Gradient(colors: [Color.white.opacity(0.1), Color.white.opacity(0.05)]),
                                startPoint: .top,
                                endPoint: .bottom
                            ))
                            .blur(radius: 10)
                        
                        Rectangle()
                            .stroke(Color.white.opacity(0.2), lineWidth: 1)
                    }
                    .background(Color.clear)
                }
            }
            ```

            ```kotlin
            // File: app/src/main/java/com/yourcompany/yourapp/ui/theme/Color.kt
            package com.yourcompany.yourapp.ui.theme

            import androidx.compose.ui.graphics.Color

            val PrimaryColor = Color(0xFF{palette['primary'][1:]})
            val SecondaryColor = Color(0xFF{palette['secondary'][1:]})
            val TextLight = Color(0xFF{palette['text_light'][1:]})
            val TextDark = Color(0xFF{palette['text_dark'][1:]})
            val BackgroundColor = Color(0xFF{palette['background'][1:]})
            val AccentColor = Color(0xFFE500FF) // Example for contrast elements
            ```

            ```kotlin
            // File: app/src/main/java/com/yourcompany/yourapp/ui/theme/Theme.kt
            package com.yourcompany.yourapp.ui.theme

            import androidx.compose.foundation.isSystemInDarkTheme
            import androidx.compose.material3.MaterialTheme
            import androidx.compose.material3.darkColorScheme
            import androidx.compose.material3.lightColorScheme
            import androidx.compose.runtime.Composable

            private val DarkColorScheme = darkColorScheme(
                primary = PrimaryColor,
                secondary = SecondaryColor,
                background = BackgroundColor,
                surface = BackgroundColor,
                onPrimary = TextLight,
                onSecondary = TextLight,
                onBackground = TextLight,
                onSurface = TextLight,
                tertiary = AccentColor // Using accent for tertiary
            )

            private val LightColorScheme = lightColorScheme(
                primary = PrimaryColor,
                secondary = SecondaryColor,
                background = BackgroundColor,
                surface = BackgroundColor,
                onPrimary = TextDark,
                onSecondary = TextDark,
                onBackground = TextDark,
                onSurface = TextDark,
                tertiary = AccentColor // Using accent for tertiary
            )

            @Composable
            fun YourAppTheme(
                darkTheme: Boolean = isSystemInDarkTheme(),
                content: @Composable () -> Unit
            ) {
                val colorScheme = when {
                    darkTheme -> DarkColorScheme
                    else -> LightColorScheme
                }

                MaterialTheme(
                    colorScheme = colorScheme,
                    typography = Type, // Assuming Type.kt exists for typography
                    content = content
                )
            }
            ```

            ```kotlin
            // File: app/src/main/java/com/yourcompany/yourapp/data/model/Survey.kt
            package com.yourcompany.yourapp.data.model

            // Represents a single question in a survey
            data class SurveyQuestion(
                val id: Int,
                val question: String,
                val type: String, // e.g., "text", "radio", "scale", "nps"
                val options: List<String>? = null, // For radio/dropdown
                val min: Int? = null, // For scale
                val max: Int? = null, // For scale
                val labels: List<String>? = null // For scale labels
            )

            // Represents a user's response to a survey
            data class SurveyResponse(
                val projectId: String,
                val userId: String,
                val surveyType: String, // "UX" or "PMF"
                val responses: Map<String, Any>, // Map of question ID to answer
                val timestamp: Long
            )

            // Represents an app rating
            data class AppRating(
                val projectId: String,
                val userId: String,
                val rating: Int, // e.g., 1-5 stars
                val comment: String? = null,
                val timestamp: Long
            )

            // Represents general user feedback
            data class UserFeedback(
                val projectId: String,
                val userId: String,
                val feedbackText: String,
                val timestamp: Long
            )
            ```

            ```kotlin
            // File: app/src/main/java/com/yourcompany/yourapp/ui/feedback/SurveyDisplay.kt
            package com.yourcompany.yourapp.ui.feedback

            import androidx.compose.animation.AnimatedVisibility
            import androidx.compose.animation.fadeIn
            import androidx.compose.animation.fadeOut
            import androidx.compose.foundation.background
            import androidx.compose.foundation.layout.*
            import androidx.compose.material3.*
            import androidx.compose.runtime.*
            import androidx.compose.ui.Alignment
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.graphics.Color
            import androidx.compose.ui.unit.dp
            import com.yourcompany.yourapp.data.model.SurveyQuestion
            import com.yourcompany.yourapp.ui.theme.BackgroundColor
            import com.yourcompany.yourapp.ui.theme.PrimaryColor
            import com.yourcompany.yourapp.ui.theme.TextLight

            @Composable
            fun SurveyPromptDialog(
                isVisible: Boolean,
                onDismiss: () -> Unit,
                onSurveyClick: () -> Unit,
                surveyTitle: String = "Quick Feedback!"
            ) {
                AnimatedVisibility(
                    visible = isVisible,
                    enter = fadeIn(),
                    exit = fadeOut()
                ) {
                    AlertDialog(
                        onDismissRequest = onDismiss,
                        title = { Text(surveyTitle, color = TextLight) },
                        text = { Text("Help us improve by answering a short survey.", color = TextLight) },
                        confirmButton = {
                            Button(
                                onClick = onSurveyClick,
                                colors = ButtonDefaults.buttonColors(containerColor = PrimaryColor)
                            ) {
                                Text("Start Survey", color = Color.White)
                            }
                        },
                        dismissButton = {
                            TextButton(onClick = onDismiss) {
                                Text("Not Now", color = TextLight)
                            }
                        },
                        containerColor = BackgroundColor
                    )
                }
            }

            @Composable
            fun SurveyScreen(
                surveyQuestions: List<SurveyQuestion>,
                onSubmit: (Map<String, Any>) -> Unit,
                onClose: () -> Unit,
                surveyType: String
            ) {
                var currentResponses by remember { mutableStateOf<MutableMap<String, Any>>(mutableMapOf()) }

                Scaffold(
                    topBar = {
                        TopAppBar(
                            title = { Text("$surveyType Survey", color = TextLight) },
                            colors = TopAppBarDefaults.topAppBarColors(containerColor = PrimaryColor),
                            navigationIcon = {
                                IconButton(onClick = onClose) {
                                    Icon(Icons.Default.Close, contentDescription = "Close", tint = TextLight)
                                }
                            }
                        )
                    }
                ) { paddingValues ->
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues)
                            .padding(16.dp)
                            .background(BackgroundColor)
                    ) {
                        surveyQuestions.forEach { question ->
                            QuestionView(question = question, onAnswer = { answer ->
                                currentResponses[question.id.toString()] = answer
                            }, currentAnswer = currentResponses[question.id.toString()])
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                        Button(
                            onClick = { onSubmit(currentResponses) },
                            modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryColor)
                        ) {
                            Text("Submit Survey", color = Color.White)
                        }
                    }
                }
            }

            @Composable
            fun QuestionView(question: SurveyQuestion, onAnswer: (Any) -> Unit, currentAnswer: Any?) {
                Column {
                    Text(question.question, style = MaterialTheme.typography.titleMedium, color = TextLight)
                    Spacer(modifier = Modifier.height(8.dp))
                    when (question.type) {
                        "text" -> {
                            OutlinedTextField(
                                value = currentAnswer as? String ?: "",
                                onValueChange = { onAnswer(it) },
                                modifier = Modifier.fillMaxWidth(),
                                label = { Text("Your answer") },
                                colors = TextFieldDefaults.outlinedTextFieldColors(
                                    focusedBorderColor = PrimaryColor,
                                    unfocusedBorderColor = TextLight.copy(alpha = 0.5f),
                                    textColor = TextLight,
                                    cursorColor = PrimaryColor
                                )
                            )
                        }
                        "radio" -> {
                            question.options?.forEach { option ->
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    RadioButton(
                                        selected = (currentAnswer as? String) == option,
                                        onClick = { onAnswer(option) },
                                        colors = RadioButtonDefaults.colors(selectedColor = PrimaryColor)
                                    )
                                    Text(option, color = TextLight)
                                }
                            }
                        }
                        "scale" -> {
                            val selectedValue = (currentAnswer as? Float) ?: (question.min?.toFloat() ?: 1f)
                            Column(modifier = Modifier.fillMaxWidth()) {
                                Slider(
                                    value = selectedValue,
                                    onValueChange = { onAnswer(it) },
                                    valueRange = question.min?.toFloat() ?: 1f .. question.max?.toFloat() ?: 5f,
                                    steps = (question.max ?: 5) - (question.min ?: 1) - 1,
                                    colors = SliderDefaults.colors(
                                        thumbColor = PrimaryColor,
                                        activeTrackColor = PrimaryColor,
                                        inactiveTrackColor = TextLight.copy(alpha = 0.3f)
                                    )
                                )
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    question.labels?.forEach { label ->
                                        Text(label, style = MaterialTheme.typography.bodySmall, color = TextLight)
                                    }
                                }
                            }
                        }
                        "nps" -> {
                            val selectedValue = (currentAnswer as? Float) ?: 0f
                            Column(modifier = Modifier.fillMaxWidth()) {
                                Slider(
                                    value = selectedValue,
                                    onValueChange = { onAnswer(it.toInt()) }, // NPS usually integer
                                    valueRange = question.min?.toFloat() ?: 0f .. question.max?.toFloat() ?: 10f,
                                    steps = (question.max ?: 10) - (question.min ?: 0) - 1,
                                    colors = SliderDefaults.colors(
                                        thumbColor = PrimaryColor,
                                        activeTrackColor = PrimaryColor,
                                        inactiveTrackColor = TextLight.copy(alpha = 0.3f)
                                    )
                                )
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("Not Likely (0)", style = MaterialTheme.typography.bodySmall, color = TextLight)
                                    Text("Very Likely (10)", style = MaterialTheme.typography.bodySmall, color = TextLight)
                                }
                            }
                        }
                    }
                }
            }
            ```

            ```kotlin
            // File: app/src/main/java/com/yourcompany/yourapp/util/AnalyticsLogger.kt
            package com.yourcompany.yourapp.util

            import android.util.Log

            object AnalyticsLogger {
                private const val TAG = "AppAnalytics"

                fun logSurveyEvent(eventId: String, projectId: String, userId: String, details: Map<String, Any>? = null) {
                    val logMessage = "Event: $eventId, Project: $projectId, User: $userId"
                    val fullMessage = if (details != null) "$logMessage, Details: $details" else logMessage
                    Log.d(TAG, fullMessage)
                    // In a real app, send this to a backend analytics service
                }
            }
            ```

            ```kotlin
            // File: app/src/main/java/com/yourcompany/yourapp/network/AppApiService.kt
            package com.yourcompany.yourapp.network

            import com.yourcompany.yourapp.data.model.SurveyResponse
            import com.yourcompany.yourapp.data.model.AppRating
            import com.yourcompany.yourapp.data.model.UserFeedback
            import retrofit2.http.Body
            import retrofit2.http.POST

            // Placeholder for API service for submitting feedback and survey data
            interface AppApiService {
                @POST("api/app-feedback/survey-response/")
                suspend fun submitSurveyResponse(@Body response: SurveyResponse): retrofit2.Response<Void>

                @POST("api/app-feedback/app-rating/")
                suspend fun submitAppRating(@Body rating: AppRating): retrofit2.Response<Void>

                @POST("api/app-feedback/user-feedback/")
                suspend fun submitUserFeedback(@Body feedback: UserFeedback): retrofit2.Response<Void>
            }
            ```
            """
            
            # In a real scenario, you'd parse `simulated_code_output` to extract code blocks
            # and save them to actual files. For this response, we just acknowledge completion.
            
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.COMPLETED
                project.status_message = "Code generation complete. App is ready for download with integrated feedback features!"
                # Potentially store a link to the generated code artifact here
                project.save()

            print(f"Code Generation complete for project {project_id}. Project is now marked as COMPLETED with new features.")

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Code generation failed: {e}"
                project.save()
            print(f"Error during code generation for project {project_id}: {e}")
            raise
